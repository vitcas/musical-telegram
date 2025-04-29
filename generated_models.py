from pydantic import BaseModel

class Archetypes(BaseModel):
    id: int
    name: str
    annotation: str
    enabled: int

class Banlists(BaseModel):
    id: int
    format: str
    created_at: str

class Cards(BaseModel):
    konami_id: int
    ydk_id: int
    name: str
    mst: str
    type_ext: int
    effect: str
    attr_id: int
    race_id: str
    level: int
    atk: int
    defesa: int
    md_rarity: str
    frelease: str
    fuel: int

class Cards_arcs(BaseModel):
    konami_id: int
    arc_id: int

class Cards_arts(BaseModel):
    konami_id: int
    ydk_id: int
    release_date: str

class Cards_bans(BaseModel):
    id: int
    konami_id: int
    restriction_id: int
    banlist_id: int

class Cards_sups(BaseModel):
    konami_id: int
    frame_id: int
    race_code: str
    elm_id: int

class Elementals(BaseModel):
    id: int
    eng_name: str
    scream: str

class Frames(BaseModel):
    id: int
    name: str
    color: str

class Products(BaseModel):
    id: int
    name: str
    card_count: int
    release_date: str

class Races(BaseModel):
    id: int
    name: str
    edo_code: str

class Restrictions(BaseModel):
    id: int
    name: str

class Types(BaseModel):
    id: int
    description: str
    frame: int
    is_extra: int

