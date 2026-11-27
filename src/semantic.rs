//! QLM-SEMANTIC-001: a world of facts and the text that states them. See
//! docs/qlm-semantic-001-plan.md.
//!
//! The names are fixed (seed 1000). The world seed assigns the facts, so
//! worlds with different seeds are entity-permuted copies of one another.

use qsystems::lm::Rng;
use std::collections::BTreeSet;

pub const COUNTRIES: usize = 24;
pub const CONTINENTS: usize = 4;
pub const PEOPLE: usize = 48;

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Rel {
    Capital,
    Located,
    Continent,
    Lives,
    LivesOn,
    /// Version 3 only: born(person → city), never the city they live in.
    Born,
}

/// One statement: a relation, its subject and object (indices into their
/// type's names), and which phrasing (0 or 1; lives-on has only 0).
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub struct Statement {
    pub rel: Rel,
    pub subject: usize,
    pub object: usize,
    pub phrasing: usize,
}

pub struct World {
    pub countries: Vec<String>,
    pub cities: Vec<String>,
    pub continents: Vec<String>,
    pub people: Vec<String>,
    /// capital[country] = city; continent[country]; lives[person] = city.
    pub capital: Vec<usize>,
    pub continent: Vec<usize>,
    pub lives: Vec<usize>,
    /// Held out: countries whose second capital phrasing is withheld;
    /// countries whose located statements are withheld; people whose
    /// lives-on statements are withheld; people seen in one lives statement
    /// only (and no lives-on).
    pub held_phrasing: BTreeSet<usize>,
    pub held_inverse: BTreeSet<usize>,
    pub held_composition: BTreeSet<usize>,
    pub held_new: BTreeSet<usize>,
    /// Version 3 only: born[person] = city.
    pub born: Option<Vec<usize>>,
}

fn shuffle<T>(v: &mut [T], r: &mut Rng) {
    for i in (1..v.len()).rev() {
        let j = (r.draw() as usize) % (i + 1);
        v.swap(i, j);
    }
}

fn names(n: usize, r: &mut Rng, used: &mut BTreeSet<String>) -> Vec<String> {
    let cons = b"bdfgklmnprstvz";
    let vows = b"aeiou";
    let mut out = Vec::new();
    while out.len() < n {
        let mut w = String::new();
        for _ in 0..3 {
            w.push(cons[(r.draw() as usize) % cons.len()] as char);
            w.push(vows[(r.draw() as usize) % vows.len()] as char);
        }
        if used.insert(w.clone()) {
            out.push(w);
        }
    }
    out
}

impl World {
    pub fn new(seed: u64) -> World {
        World::with_holdout(seed, true)
    }

    /// `by_city` false is the first design, which held people out one by
    /// one and left a city-mate shortcut. It is kept only to study that
    /// shortcut (`qlm shortcut`).
    pub fn with_holdout(seed: u64, by_city: bool) -> World {
        let mut nr = Rng(1000);
        let mut used: BTreeSet<String> =
            ["has", "capital", "the", "of", "is", "located", "in", "a", "city", "lies", "on", "lives", "from"]
                .iter()
                .map(|s| s.to_string())
                .collect();
        let countries = names(COUNTRIES, &mut nr, &mut used);
        let cities = names(COUNTRIES, &mut nr, &mut used);
        let continents = names(CONTINENTS, &mut nr, &mut used);
        let people = names(PEOPLE, &mut nr, &mut used);
        let mut r = Rng(seed.wrapping_mul(0x2545_F491_4F6C_DD1D) ^ 0x5EED);
        // Facts, balanced: 6 countries per continent, 2 people per city.
        let mut capital: Vec<usize> = (0..COUNTRIES).collect();
        shuffle(&mut capital, &mut r);
        let mut order: Vec<usize> = (0..COUNTRIES).collect();
        shuffle(&mut order, &mut r);
        let mut continent = vec![0; COUNTRIES];
        for (k, &c) in order.iter().enumerate() {
            continent[c] = k / (COUNTRIES / CONTINENTS);
        }
        let mut porder: Vec<usize> = (0..PEOPLE).collect();
        shuffle(&mut porder, &mut r);
        let mut lives = vec![0; PEOPLE];
        for (k, &p) in porder.iter().enumerate() {
            lives[p] = k / 2;
        }
        // Held out, disjoint. Phrasing and inverse: 6 countries each.
        let mut cs: Vec<usize> = (0..COUNTRIES).collect();
        shuffle(&mut cs, &mut r);
        let held_phrasing: BTreeSet<usize> = cs[..6].iter().copied().collect();
        let held_inverse: BTreeSet<usize> = cs[6..12].iter().copied().collect();
        // Composition and new entity are held out by city, both residents
        // together, so that no city-mate's statement gives the answer away
        // (a change after a first result: docs/qlm-semantic-001-plan.md).
        // Composition: the residents of 2 cities per continent (16 people).
        // New entity: the residents of 2 further cities (4 people).
        let mut cities_by_cont: Vec<Vec<usize>> = vec![Vec::new(); CONTINENTS];
        let mut order_c: Vec<usize> = (0..COUNTRIES).collect();
        shuffle(&mut order_c, &mut r);
        for &c in &order_c {
            cities_by_cont[continent[c]].push(capital[c]);
        }
        let comp_cities: BTreeSet<usize> = cities_by_cont.iter().flat_map(|v| v[..2].iter().copied()).collect();
        let new_cities: BTreeSet<usize> = order_c.iter().map(|&c| capital[c]).filter(|k| !comp_cities.contains(k)).take(2).collect();
        let (held_composition, held_new) = if by_city {
            (
                (0..PEOPLE).filter(|p| comp_cities.contains(&lives[*p])).collect::<BTreeSet<usize>>(),
                (0..PEOPLE).filter(|p| new_cities.contains(&lives[*p])).collect::<BTreeSet<usize>>(),
            )
        } else {
            // The first design: 3 people per continent, then 4 more people.
            let cont_of = |p: usize| continent[capital.iter().position(|&k| k == lives[p]).unwrap()];
            let mut ps: Vec<usize> = (0..PEOPLE).collect();
            shuffle(&mut ps, &mut r);
            let mut comp = BTreeSet::new();
            let mut per = vec![0; CONTINENTS];
            for &p in &ps {
                if per[cont_of(p)] < 3 {
                    per[cont_of(p)] += 1;
                    comp.insert(p);
                }
            }
            let new: BTreeSet<usize> = ps.iter().filter(|p| !comp.contains(p)).take(4).copied().collect();
            (comp, new)
        };
        World { countries, cities, continents, people, capital, continent, lives, held_phrasing, held_inverse, held_composition, held_new, born: None }
    }

    /// Version 3: the version-2 world (same seed, same facts, same holdouts)
    /// with a birth city for every person: two births per city, never the
    /// city the person lives in. Drawn after everything else, so nothing of
    /// version 2 changes.
    pub fn v3(seed: u64) -> World {
        let mut w = World::new(seed);
        let mut r = Rng(seed.wrapping_mul(0x9E37_79B9_7F4A_7C15) ^ 0xB0B0);
        loop {
            let mut slots: Vec<usize> = (0..PEOPLE).map(|k| k / 2).collect();
            shuffle(&mut slots, &mut r);
            if (0..PEOPLE).all(|p| slots[p] != w.lives[p]) {
                w.born = Some(slots);
                return w;
            }
        }
    }

    /// The country whose capital is `city`.
    pub fn country_of(&self, city: usize) -> usize {
        self.capital.iter().position(|&k| k == city).unwrap()
    }

    /// The continent a person lives on: lives, then located, then continent.
    pub fn lives_on(&self, person: usize) -> usize {
        self.continent[self.country_of(self.lives[person])]
    }

    pub fn render(&self, s: &Statement) -> String {
        let (c, k, t, p) = (&self.countries, &self.cities, &self.continents, &self.people);
        match (s.rel, s.phrasing) {
            (Rel::Capital, 0) => format!("{} has capital {} .", c[s.subject], k[s.object]),
            (Rel::Capital, _) => format!("the capital of {} is {} .", c[s.subject], k[s.object]),
            (Rel::Located, 0) => format!("{} is located in {} .", k[s.subject], c[s.object]),
            (Rel::Located, _) => format!("{} is a city of {} .", k[s.subject], c[s.object]),
            (Rel::Continent, 0) => format!("{} is in {} .", c[s.subject], t[s.object]),
            (Rel::Continent, _) => format!("{} lies on {} .", c[s.subject], t[s.object]),
            (Rel::Lives, 0) => format!("{} lives in {} .", p[s.subject], k[s.object]),
            (Rel::Lives, _) => format!("{} is from {} .", p[s.subject], k[s.object]),
            (Rel::LivesOn, _) => format!("{} lives on {} .", p[s.subject], t[s.object]),
            (Rel::Born, 0) => format!("{} was born in {} .", p[s.subject], k[s.object]),
            (Rel::Born, _) => format!("{} is a native of {} .", p[s.subject], k[s.object]),
        }
    }

    /// Whether a statement may appear in training.
    pub fn allowed(&self, s: &Statement) -> bool {
        match s.rel {
            Rel::Capital => !(s.phrasing == 1 && self.held_phrasing.contains(&s.subject)),
            Rel::Located => !self.held_inverse.contains(&self.country_of(s.subject)),
            Rel::Continent => true,
            // A new-entity person keeps only the first lives phrasing.
            Rel::Lives => !(s.phrasing == 1 && self.held_new.contains(&s.subject)),
            Rel::LivesOn => !self.held_composition.contains(&s.subject) && !self.held_new.contains(&s.subject),
            Rel::Born => true,
        }
    }

    fn st(rel: Rel, subject: usize, object: usize, r: &mut Rng) -> Statement {
        let phrasing = if rel == Rel::LivesOn { 0 } else { (r.draw() % 2) as usize };
        Statement { rel, subject, object, phrasing }
    }

    /// A random text of one to three true statements, every one allowed.
    /// A new-entity person appears in no random text: their one lives
    /// statement is added once, by `corpus`. A held-out composition
    /// person's name never shares a text with their continent's name.
    pub fn text(&self, r: &mut Rng) -> Vec<Statement> {
        loop {
            let kind = r.draw() % if self.born.is_some() { 12 } else { 10 };
            let c = (r.draw() as usize) % COUNTRIES;
            let p = (r.draw() as usize) % PEOPLE;
            let k = self.capital[c];
            let t = self.continent[c];
            let text: Vec<Statement> = match kind {
                0 => vec![World::st(Rel::Capital, c, k, r)],
                1 => vec![World::st(Rel::Located, k, c, r)],
                2 => vec![World::st(Rel::Continent, c, t, r)],
                3 => vec![World::st(Rel::Lives, p, self.lives[p], r)],
                4 => vec![World::st(Rel::LivesOn, p, self.lives_on(p), r)],
                5 => vec![World::st(Rel::Capital, c, k, r), World::st(Rel::Continent, c, t, r)],
                6 => vec![World::st(Rel::Located, k, c, r), World::st(Rel::Continent, c, t, r)],
                7 => {
                    let k = self.lives[p];
                    let c = self.country_of(k);
                    vec![World::st(Rel::Lives, p, k, r), World::st(Rel::Located, k, c, r), World::st(Rel::Continent, c, self.continent[c], r)]
                }
                8 => vec![World::st(Rel::Lives, p, self.lives[p], r), World::st(Rel::LivesOn, p, self.lives_on(p), r)],
                10 => vec![World::st(Rel::Born, p, self.born.as_ref().unwrap()[p], r)],
                11 => vec![World::st(Rel::Lives, p, self.lives[p], r), World::st(Rel::Born, p, self.born.as_ref().unwrap()[p], r)],
                _ => {
                    let k = self.lives[p];
                    vec![World::st(Rel::Lives, p, k, r), World::st(Rel::Located, k, self.country_of(k), r)]
                }
            };
            let people_in: Vec<usize> = text
                .iter()
                .filter(|s| matches!(s.rel, Rel::Lives | Rel::LivesOn | Rel::Born))
                .map(|s| s.subject)
                .collect();
            if people_in.iter().any(|q| self.held_new.contains(q)) {
                continue;
            }
            let continents_in: BTreeSet<usize> = text
                .iter()
                .filter(|s| matches!(s.rel, Rel::Continent | Rel::LivesOn))
                .map(|s| s.object)
                .collect();
            if people_in.iter().any(|q| self.held_composition.contains(q) && continents_in.contains(&self.lives_on(*q))) {
                continue;
            }
            // A held-out inverse: the capital may never come before its
            // country anywhere in a text, in any statement. (The first
            // version allowed "C has capital K . C is in T .", whose "K . C"
            // gave the inverse away: docs/qlm-semantic-001-plan.md.)
            let leaks = text.iter().enumerate().any(|(i, a)| {
                matches!(a.rel, Rel::Capital) && self.held_inverse.contains(&a.subject)
                    && text[i + 1..].iter().any(|b| match b.rel {
                        Rel::Capital | Rel::Continent => b.subject == a.subject,
                        Rel::Located => b.object == a.subject,
                        _ => false,
                    })
            });
            if !leaks && text.iter().all(|s| self.allowed(s)) {
                return text;
            }
        }
    }

    pub fn line(&self, text: &[Statement]) -> String {
        text.iter().map(|s| self.render(s)).collect::<Vec<_>>().join(" ")
    }

    /// `n` training texts, then the one lives statement of each new-entity
    /// person.
    pub fn corpus(&self, n: usize, r: &mut Rng) -> Vec<String> {
        let mut out: Vec<String> = (0..n).map(|_| self.line(&self.text(r))).collect();
        for &p in &self.held_new {
            out.push(self.render(&Statement { rel: Rel::Lives, subject: p, object: self.lives[p], phrasing: 0 }));
        }
        out
    }

    /// The test items: (test, prefix, answer, type of the answer). Seen
    /// facts are included as the control.
    pub fn tests(&self) -> Vec<(String, String, String, String)> {
        let mut t = Vec::new();
        let (c, k, tt, p) = (&self.countries, &self.cities, &self.continents, &self.people);
        for x in 0..COUNTRIES {
            let cap = &k[self.capital[x]];
            let phr = if self.held_phrasing.contains(&x) { "phrasing" } else { "seen" };
            t.push((phr.into(), format!("the capital of {} is", c[x]), cap.clone(), "city".into()));
            if !self.held_phrasing.contains(&x) {
                t.push(("seen".into(), format!("{} has capital", c[x]), cap.clone(), "city".into()));
            }
            let inv = if self.held_inverse.contains(&x) { "inverse" } else { "seen" };
            t.push((inv.into(), format!("{cap} is located in"), c[x].clone(), "country".into()));
            t.push((inv.into(), format!("{cap} is a city of"), c[x].clone(), "country".into()));
        }
        for q in 0..PEOPLE {
            let test = if self.held_composition.contains(&q) {
                "composition"
            } else if self.held_new.contains(&q) {
                "new entity"
            } else {
                "seen"
            };
            t.push((test.into(), format!("{} lives on", p[q]), tt[self.lives_on(q)].clone(), "continent".into()));
        }
        t
    }
}
