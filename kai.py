import random, hashlib
from collections import defaultdict, Counter
from database import DATABASE_URL
from sqlalchemy import create_engine, text
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import sessionmaker

MM_SIZE = 20
ST_SIZE = 10
EX_SIZE = 15

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def gerar_hash():
    return hashlib.sha1(str(random.random()).encode()).hexdigest()[:8]

def calculate_majority(counter, total):
    if not counter or total == 0:
        return None, 0.0
    top = max(counter, key=counter.get)
    return top, (counter[top] / total) * 100

def among_us(mst_data):
    wanted = [4113,4129,4161,4193,4257,5153,12321,16781329,16781345,33558561]
    for mst in mst_data:
        for (type_ext, desc), count in mst_data[mst].items():
            if type_ext in wanted:
                return True
    return False

def build_query(arc_id, races_elms, frames):
    preq = """
        SELECT cv.ydk_id, cv.konami_id, cv.type as mst, cv.is_extra 
        FROM cards_view cv
        INNER JOIN cards_sups cs ON cv.konami_id = cs.konami_id
    """
    print(f"Gerando query para o arquétipo {arc_id}...")   
    query_main = ""
    query_extra = ""
    if frames:
        yaux = " OR ".join([f"frame_id = {frame_id}" for frame_id in frames])
    if races_elms: 
        conditions = [] 
        if len(races_elms) == 2:
            aux = " AND ".join(races_elms)
            conditions.append(f"({aux})")  
        for condition in races_elms:
            if "race_code" in condition:
                conditions.append(f"({condition} AND elm_id IS NULL)")
            elif "elm_id" in condition:
                conditions.append(f"(race_code IS NULL AND {condition})")         
        if conditions:
            xaux = " OR ".join(conditions)
            query_main += f" WHERE (is_extra = 0 AND ({xaux}))"
            if frames:
                query_extra += f" \nOR (is_extra = 1 AND ({xaux}) AND ({yaux}))" 
            else:
                query_extra += f" \nOR (is_extra = 1 AND ({xaux}) AND frame_id = 10)" 
    elif frames:
        query_extra += f" WHERE (is_extra = 1 AND ({yaux}))"
    full_query = f"{preq}{query_main}{query_extra}"
    print(f"Query gerada:\n{query_main}{query_extra}")
    return full_query

def deck_analysis(arc_id):
    print(f"Analisando arquétipo {arc_id}...")   
    with SessionLocal() as session:
        # Consulta para recuperar informações sobre as cartas
        result = session.execute(text("""
            SELECT c.type_ext, c.race_id, c.attr_id, t.is_extra, t.frame, c.mst, t.description
            FROM cards c
            JOIN cards_arcs ca ON ca.konami_id = c.konami_id
            JOIN types t ON t.id = c.type_ext
            WHERE ca.arc_id = :arc_id
        """), {"arc_id": arc_id}).fetchall()     
        if not result:
            return {'error': f'Nenhuma carta encontrada para o arquétipo {arc_id}'}
        total_cards = len(result)
        print(f"total: {total_cards}")
        # Contadores para raça, atributo, frame, MST
        race_counter = Counter()
        attr_counter = Counter()
        frame_counter = Counter()
        mst_data = defaultdict(Counter)
        mst_counter = Counter() 
        for type_ext, race_id, attr_id, is_extra, frame, mst, desc in result:
            race_counter[race_id] += 1
            attr_counter[attr_id] += 1
            mst_data[mst][(type_ext, desc)] += 1
            mst_counter[mst] += 1
            if is_extra:
                frame_counter[frame] += 1
        # Calcular maioria de raça e atributo
        main_race, main_race_pct = calculate_majority(race_counter, total_cards)
        main_attr, main_attr_pct = calculate_majority(attr_counter, total_cards)
        # Contagem organizada por mst
        for mst in mst_data:
            print(f"{mst}: {mst_counter[mst]}")
            for (type_ext, desc), count in mst_data[mst].items():
                print(f"  {type_ext} - {desc}: {count}")
        resultado = among_us(mst_data)
        print(f"Tem tuner? {resultado}")
        print(f"extra deck frames: {frame_counter}")
        # Filtro de raça e atributo
        race_attr_filter = []
        if main_race_pct >= 34 and main_race != '0':
            race_attr_filter.append(f"race_code LIKE '{main_race}'")
        if main_attr_pct >= 34 and int(main_attr) < 8:
            race_attr_filter.append(f"elm_id = {main_attr}")
        # Filtro de frames extra
        extra_frames = [frame for frame, count in frame_counter.items()]      
    # Gerar a query final
    finalq = build_query(arc_id, race_attr_filter, extra_frames)
    return finalq

def gimme_cards(custom_query):
    with SessionLocal() as session:
        result = session.execute(text(custom_query))
        return result.fetchall()    

def gimme_extra():
    query = """
        SELECT cv.ydk_id, cv.konami_id, cv.type as mst, cv.is_extra 
        FROM cards_view cv
        INNER JOIN cards_sups cs ON cv.konami_id = cs.konami_id
        WHERE frame_id = 10 AND elm_id IS NULL AND cs.race_code IS NULL AND is_extra = 1
    """
    extra_cards = gimme_cards(query)
    return extra_cards   

def gimme_staples():
    query = "SELECT ydk_id, konami_id, type as mst, is_extra FROM cards_view WHERE arc_id = 473"
    staples = gimme_cards(query)
    return staples

def its_over(cquery=""):
    preq = "SELECT konami_id, mst FROM beta_view WHERE mst = :mst" 
    with SessionLocal() as session:
        # Executa as consultas para 'monster', 'spell' e 'trap'
        m = session.execute(text(preq), {"mst": "monster"}).fetchall()
        s = session.execute(text(preq), {"mst": "spell"}).fetchall()
        t = session.execute(text(preq), {"mst": "trap"}).fetchall()
    return m, s, t

def split_card_types(cards):
    main, extra, spells, traps = [], [], [], []
    for konami_id, mst, is_extra in cards:
        if "monster" in mst:
            (extra if int(is_extra) > 0 else main).append((konami_id))
        elif "spell" in mst:
            spells.append((konami_id))
        elif "trap" in mst:
            traps.append((konami_id))
    return main, extra, spells, traps

def fill_section(target, needed, pool):
    if len(target) >= needed:
        return
    used = set(target)
    for card in pool:
        if card not in used:
            target.append(card)
            used.add(card)
            if len(target) >= needed:
                break

def fill_deck(cards, arcid=0):
    # step 1 - popula a amostra do modo
    random.shuffle(cards)
    main, extra, spells, traps = split_card_types(cards)   
    main = main[:MM_SIZE]
    spells = spells[:ST_SIZE]
    traps = traps[:ST_SIZE]
    extra = extra[:EX_SIZE]
    # step 2 - popula a amostra complementar
    dm, ds, dt = its_over() 
    random.shuffle(dm)
    random.shuffle(ds)
    random.shuffle(dt)        
    dex = gimme_extra()
    random.shuffle(dex)
    # rotina apenas para arquetipos (pre-complementar)
    if (arcid > 0):
        query = deck_analysis(arcid)      
        arcbase = gimme_cards(query)
        random.shuffle(arcbase)
        m2, e2, s2, t2 = split_card_types(arcbase)
        fill_section(main, MM_SIZE, m2)
        fill_section(spells, ST_SIZE, s2)
        fill_section(traps, ST_SIZE, t2)   
        fill_section(extra, EX_SIZE, e2)       
    # rotina de preenchimento padrão
    fill_section(main, MM_SIZE, dm)
    fill_section(spells, ST_SIZE, ds)
    fill_section(traps, ST_SIZE, dt)   
    fill_section(extra, EX_SIZE, dex)
    return main + spells + traps, extra

def generate_side():
    cards = gimme_staples()
    random.shuffle(cards)
    side = cards[:15]
    return side

def archetype_mode():
    with SessionLocal() as session:
        arc_result = session.execute(text("SELECT id, name FROM archetypes ORDER BY RANDOM() LIMIT 1")).fetchone()
        arc_id, name = arc_result       
        # Consulta para pegar as cartas associadas ao arquétipo
        query = f"SELECT cv.ydk_id, konami_id, type, is_extra FROM cards_view WHERE arc_id = {arc_id}"
        cards = gimme_cards(query)  
    madeck, exdeck = fill_deck(cards, arc_id)
    return madeck, exdeck, name

def arc_forced(acid, name):
    query = f"SELECT cv.ydk_id, konami_id, type, is_extra FROM cards_view WHERE arc_id = :arc_id"
    cards = gimme_cards(query, {"arc_id": acid})  # Passando o parâmetro arc_id
    madeck, exdeck = fill_deck(cards, acid)
    return madeck, exdeck, name

def element_mode():
    with SessionLocal() as session:
        # Consulta para pegar os 6 primeiros elementos (excluindo o id=7)
        result = session.execute(text("SELECT id, eng_name FROM elementals WHERE id != 7 ORDER BY id LIMIT 6")).fetchall()
        # Escolhe um elemento aleatório
        element = random.choice(result)
        attr_id, attr_name = element 
        preq = """
            SELECT cv.ydk_id, cv.konami_id, cv.type, cv.is_extra 
            FROM cards_view cv
            INNER JOIN cards_sups cs ON cv.konami_id = cs.konami_id
        """
        query = f"{preq} WHERE cs.elm_id = {attr_id}"
        cards = gimme_cards(query)
    madeck, exdeck = fill_deck(cards)
    return madeck, exdeck, f"element_{attr_name}"

def race_mode():
    with SessionLocal() as session:
        # Consulta para pegar uma raça aleatória
        result = session.execute(text("SELECT edo_code, name FROM races ORDER BY RANDOM() LIMIT 1")).fetchone() 
        if not result:
            return {'error': 'Nenhuma raça encontrada'}  
        race_id, race_name = result
        preq = """
            SELECT cv.ydk_id, cv.konami_id, cv.type, cv.is_extra 
            FROM cards_view cv
            INNER JOIN cards_sups cs ON cv.konami_id = cs.konami_id
        """
        query = f"{preq} WHERE cs.race_code LIKE '{race_id}'"
        cards = gimme_cards(query)
    madeck, exdeck = fill_deck(cards)
    return madeck, exdeck, f"race_{race_name.lower()}"

def mount_ydk(main, extra, side, name):
    lines = ["#created by kaiba_ai", f"#deck_name: {name}", "#main"]
    for c in main:
        lines.append(str(c[0]) if isinstance(c, Row) else str(c))
    lines.append("#extra")
    for c in extra:
        lines.append(str(c[0]) if isinstance(c, Row) else str(c))
    lines.append("!side")
    for c in side:
        lines.append(str(c[0]) if isinstance(c, Row) else str(c))
    return "\n".join(lines)

def mode_select(mode):
    match mode:
        case 1: 
            print("archetype_mode")
            main, extra, name = archetype_mode()
        case 2: 
            print("element_mode")
            main, extra, name = element_mode()
        case 3: 
            print("race_mode")
            main, extra, name = race_mode()
    side = generate_side() 
    content = mount_ydk(main, extra, side, name)
    print(content)
    return content

if __name__ == "__main__":
    mode = random.choice([1, 2, 3])
    mode_select(mode)
