from .card import Card
from .actions import (
    gain_life_action, explore_action, draw_card_action, creature_dies_action,
    lose_life_generic_action, scry_action, add_counter_action, create_token_action,
    add_counter_to_all_creatures_action, maybe_create_token_action,
    dark_confidant_draw_action, elenda_death_token_action, esper_sentinel_draw_action,
    essence_channeler_death_action, kambal_life_gain_action, leonin_elder_life_gain_action,
    mother_of_runes_counter_removal_action, ocelot_pride_end_of_turn_action,
    selfless_spirit_counter_action, sorin_life_gain_action, spectrum_sentinel_land_action,
    aetherflux_reservoir_life_gain_action, cleric_class_extra_life_action
)

CARD_DATABASE = {
    # Lands
    "Plains": lambda: Card("Plains", "Land", colors=["W"]),
    "Swamp": lambda: Card("Swamp", "Land", colors=["B"]),
    "Barren Moor": lambda: Card(
        "Barren Moor", "Land", colors=["B"], enters_tapped=True
    ),
    "Brightclimb Pathway": lambda: Card(
        "Brightclimb Pathway", "Land", colors=["W"]
    ),
    "Caves of Koilos": lambda: Card(
        "Caves of Koilos", "Land", colors=["W", "B"]
    ),
    "Command Tower": lambda: Card(
        "Command Tower", "Land", colors=["W", "B"]
    ),
    "Exotic Orchard": lambda: Card(
        "Exotic Orchard", "Land", colors=["W", "B"]
    ),
    "Fetid Heath": lambda: Card(
        "Fetid Heath", "Land", colors=["W", "B"]
    ),
    "Godless Shrine": lambda: Card(
        "Godless Shrine", "Land", colors=["W", "B"], etb_cost_life=2
    ),
    "Isolated Chapel": lambda: Card(
        "Isolated Chapel", "Land", colors=["W", "B"]
    ),
    "Marsh Flats": lambda: Card(
        "Marsh Flats", "Land", colors=["W", "B"]
    ),
    "Radiant Fountain": lambda: Card(
        "Radiant Fountain", "Land", colors=["W"], enters_tapped=True,
        triggers=[{"event": "self_etb", "action": gain_life_action, "params": {"amount": 2}}]
    ),
    "Rogue's Passage": lambda: Card(
        "Rogue's Passage", "Land", colors=["C"]
    ),
    "Secluded Steppe": lambda: Card(
        "Secluded Steppe", "Land", colors=["W"], enters_tapped=True
    ),
    "Shattered Sanctum": lambda: Card(
        "Shattered Sanctum", "Land", colors=["W", "B"]
    ),
    "Shineshadow Snarl": lambda: Card(
        "Shineshadow Snarl", "Land", colors=["W", "B"]
    ),
    "Shizo, Death's Storehouse": lambda: Card(
        "Shizo, Death's Storehouse", "Land", colors=["B"]
    ),
    "Silent Clearing": lambda: Card(
        "Silent Clearing", "Land", colors=["W", "B"]
    ),
    "Tainted Field": lambda: Card(
        "Tainted Field", "Land", colors=["W", "B"]
    ),
    "Urborg, Tomb of Yawgmoth": lambda: Card(
        "Urborg, Tomb of Yawgmoth", "Land", colors=["B"]
    ),
    "Vault of Champions": lambda: Card(
        "Vault of Champions", "Land", colors=["W", "B"]
    ),
    "Vault of the Archangel": lambda: Card(
        "Vault of the Archangel", "Land", colors=["C"]
    ),

    # Creatures
    "Aerith Gainsborough": lambda: Card(
        "Aerith Gainsborough", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=2, toughness=2,
        triggers=[{"event": "life_gained", "action": add_counter_action, "params": {"counter_type": "+1/+1", "amount": 1}}]
    ),
    "Amalia Benavides Aguirre": lambda: Card(
        "Amalia Benavides Aguirre", "Creature", cost={"W": 1, "B": 1, "C": 0}, power=1, toughness=3,
        triggers=[{"event": "life_gained", "action": explore_action, "params": {}}]
    ),
    "Archangel of Thune": lambda: Card(
        "Archangel of Thune", "Creature", cost={"W": 2, "B": 0, "C": 3}, power=3, toughness=4,
        triggers=[{"event": "life_gained", "action": add_counter_to_all_creatures_action, "params": {"counter_type": "+1/+1", "amount": 1}}]
    ),
    "Archivist of Oghma": lambda: Card(
        "Archivist of Oghma", "Creature", cost={"W": 1, "B": 0, "C": 1}, power=2, toughness=2,
        triggers=[{"event": "opp_searched_library", "action": draw_card_action, "params": {"amount": 1}}, {"event": "opp_searched_library", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Auriok Champion": lambda: Card(
        "Auriok Champion", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=1,
        triggers=[{"event": "any_creature_etb", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Blood Artist": lambda: Card(
        "Blood Artist", "Creature", cost={"W": 0, "B": 1, "C": 0}, power=0, toughness=1,
        triggers=[{"event": "creature_dies", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Charismatic Conqueror": lambda: Card(
        "Charismatic Conqueror", "Creature", cost={"W": 1, "B": 1, "C": 0}, power=2, toughness=2,
        triggers=[{"event": "opp_creature_etb", "action": maybe_create_token_action, "params": {}}]
    ),
    "Cruel Celebrant": lambda: Card(
        "Cruel Celebrant", "Creature", cost={"W": 0, "B": 1, "C": 0}, power=1, toughness=2,
        triggers=[{"event": "creature_dies", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Dark Confidant": lambda: Card(
        "Dark Confidant", "Creature", cost={"W": 0, "B": 1, "C": 0}, power=2, toughness=1,
        triggers=[{"event": "start_of_turn", "action": dark_confidant_draw_action, "params": {}}]
    ),
    "Daxos, Blessed by the Sun": lambda: Card(
        "Daxos, Blessed by the Sun", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=2, toughness=0,
        triggers=[{"event": "my_creature_etb", "action": gain_life_action, "params": {"amount": 1}}, {"event": "my_creature_dies", "action": draw_card_action, "params": {"amount": 1}}]
    ),
    "Deathgreeter": lambda: Card(
        "Deathgreeter", "Creature", cost={"W": 0, "B": 1, "C": 0}, power=1, toughness=1,
        triggers=[{"event": "creature_dies", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Delney, Streetwise Lookout": lambda: Card(
        "Delney, Streetwise Lookout", "Creature", cost={"W": 1, "B": 0, "C": 1}, power=2, toughness=2,
        triggers=[]
    ),
    "Elas il-Kor, Sadistic Pilgrim": lambda: Card(
        "Elas il-Kor, Sadistic Pilgrim", "Creature", cost={"W": 0, "B": 1, "C": 0}, power=2, toughness=2,
        triggers=[{"event": "my_creature_etb", "action": lose_life_generic_action, "params": {"all_opponents": True}}]
    ),
    "Elenda's Hierophant": lambda: Card(
        "Elenda's Hierophant", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=4,
        triggers=[{"event": "self_dies", "action": elenda_death_token_action, "params": {}}]
    ),
    "Esper Sentinel": lambda: Card(
        "Esper Sentinel", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=1,
        triggers=[{"event": "opp_plays_card", "action": esper_sentinel_draw_action, "params": {"esper_pay_rate": 0.2}}]
    ),
    "Essence Channeler": lambda: Card(
        "Essence Channeler", "Creature", cost={"W": 0, "B": 0, "C": 2}, power=2, toughness=1,
        triggers=[
            {"event": "any_creature_etb", "action": scry_action, "params": {"amount": 1}},
            {"event": "self_dies", "action": essence_channeler_death_action, "params": {}}
        ]
    ),
    "Guide of Souls": lambda: Card(
        "Guide of Souls", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=2,
        triggers=[{"event": "my_creature_etb", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Heliod, Sun-Crowned": lambda: Card(
        "Heliod, Sun-Crowned", "Creature", cost={"W": 1, "B": 0, "C": 2}, power=5, toughness=5,
        triggers=[{"event": "life_gained", "action": add_counter_action, "params": {"counter_type": "+1/+1", "amount": 1}}]
    ),
    "Hinterland Sanctifier": lambda: Card(
        "Hinterland Sanctifier", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=2, toughness=1,
        triggers=[{"event": "my_creature_etb", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Kambal, Consul of Allocation": lambda: Card(
        "Kambal, Consul of Allocation", "Creature", cost={"W": 1, "B": 1, "C": 0}, power=2, toughness=3,
        triggers=[{"event": "opp_plays_card", "action": kambal_life_gain_action, "params": {}}]
    ),
    "Karlov of the Ghost Council": lambda: Card(
        "Karlov of the Ghost Council", "Creature", cost={"W": 1, "B": 1, "C": 0}, power=2, toughness=2,
        triggers=[{"event": "life_gained", "action": add_counter_action, "params": {"counter_type": "+1/+1", "amount": 2}}]
    ),
    "Leonin Elder": lambda: Card(
        "Leonin Elder", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=1,
        triggers=[{"event": "any_plays_card", "action": leonin_elder_life_gain_action, "params": {}}]
    ),
    "Lotho, Corrupt Shirriff": lambda: Card(
        "Lotho, Corrupt Shirriff", "Creature", cost={"W": 1, "B": 1, "C": 0}, power=2, toughness=1,
        triggers=[]
    ),
    "Lunarch Veteran": lambda: Card(
        "Lunarch Veteran", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=1,
        triggers=[{"event": "my_creature_etb", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Lurrus of the Dream-Den": lambda: Card(
        "Lurrus of the Dream-Den", "Creature", cost={"W": 1, "B": 1, "C": 0}, power=3, toughness=2,
        triggers=[{"event": "any_creature_etb", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Marauding Blight-Priest": lambda: Card(
        "Marauding Blight-Priest", "Creature", cost={"W": 0, "B": 1, "C": 1}, power=3, toughness=2,
        triggers=[{"event": "life_gained", "action": lose_life_generic_action, "params": {"all_opponents": True}}]
    ),
    "Mother of Runes": lambda: Card(
        "Mother of Runes", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=1,
        triggers=[{"event": "opp_plays_removal", "action": mother_of_runes_counter_removal_action, "params": {}}]
    ),
    "Ocelot Pride": lambda: Card(
        "Ocelot Pride", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=2, toughness=2,
        triggers=[{"event": "end_of_turn", "action": ocelot_pride_end_of_turn_action, "params": {}}]
    ),
    "Selfless Spirit": lambda: Card(
        "Selfless Spirit", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=2, toughness=1,
        triggers=[
            {"event": "opp_plays_removal", "action": selfless_spirit_counter_action, "params": {}},
            {"event": "opp_plays_boardwipe", "action": selfless_spirit_counter_action, "params": {}}
        ]
    ),
    "Serra Ascendant": lambda: Card(
        "Serra Ascendant", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=1,
        triggers=[{"event": "self_etb", "action": add_counter_action, "params": {"counter_type": "+1/+1", "amount": 5}}]
    ),
    "Soul Warden": lambda: Card(
        "Soul Warden", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=1,
        triggers=[{"event": "any_creature_etb", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Soul's Attendant": lambda: Card(
        "Soul's Attendant", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=1,
        triggers=[{"event": "any_creature_etb", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Spectrum Sentinel": lambda: Card(
        "Spectrum Sentinel", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=2,
        triggers=[{"event": "opp_plays_land", "action": spectrum_sentinel_land_action, "params": {}}]
    ),
    "Starscape Cleric": lambda: Card(
        "Starscape Cleric", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=2, toughness=2,
        triggers=[{"event": "life_gained", "action": lose_life_generic_action, "params": {"all_opponents": True}}]
    ),
    "Suture Priest": lambda: Card(
        "Suture Priest", "Creature", cost={"W": 1, "B": 0, "C": 0}, power=1, toughness=2,
        triggers=[{"event": "my_creature_etb", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Voice of the Blessed": lambda: Card(
        "Voice of the Blessed", "Creature", cost={"W": 1, "B": 0, "C": 1}, power=2, toughness=2,
        triggers=[{"event": "life_gained", "action": add_counter_action, "params": {"counter_type": "+1/+1", "amount": 1}}]
    ),
    "Vito, Thorn of the Dusk Rose": lambda: Card(
        "Vito, Thorn of the Dusk Rose", "Creature", cost={"W": 0, "B": 1, "C": 1}, power=1, toughness=3,
        triggers=[{"event": "life_gained", "action": lose_life_generic_action, "params": {}}]
    ),
    "Zulaport Cutthroat": lambda: Card(
        "Zulaport Cutthroat", "Creature", cost={"W": 0, "B": 1, "C": 0}, power=1, toughness=1,
        triggers=[{"event": "my_creature_dies", "action": lose_life_generic_action, "params": {}}]
    ),

    # Artifacts
    "Aetherflux Reservoir": lambda: Card(
        "Aetherflux Reservoir", "Artifact", cost={"W": 0, "B": 0, "C": 4},
        triggers=[{"event": "my_plays_card", "action": aetherflux_reservoir_life_gain_action, "params": {}}]
    ),
    "Lightning Greaves": lambda: Card(
        "Lightning Greaves", "Artifact", cost={"W": 0, "B": 0, "C": 2}
    ),
    "Mox Amber": lambda: Card(
        "Mox Amber", "Artifact", cost={"W": 0, "B": 0, "C": 0},
        is_land=True, colors=["W", "B"]
    ),
    "Orzhov Signet": lambda: Card(
        "Orzhov Signet", "Artifact", cost={"W": 0, "B": 0, "C": 2},
        is_land=True, colors=["W", "B"]
    ),
    "Sensei's Divining Top": lambda: Card(
        "Sensei's Divining Top", "Artifact", cost={"W": 0, "B": 0, "C": 1},
        triggers=[{"event": "my_creature_etb", "action": scry_action, "params": {"amount": 1}}]
    ),
    "Shadowspear": lambda: Card(
        "Shadowspear", "Artifact", cost={"W": 0, "B": 0, "C": 1}
    ),
    "Skullclamp": lambda: Card(
        "Skullclamp", "Artifact", cost={"W": 0, "B": 0, "C": 1}
    ),
    "Smothering Tithe": lambda: Card(
        "Smothering Tithe", "Artifact", cost={"W": 1, "B": 0, "C": 2},
        triggers=[]
    ),
    "Sol Ring": lambda: Card(
        "Sol Ring", "Artifact", cost={"W": 0, "B": 0, "C": 2},
        is_land=True, colors=["C"]
    ),

    # Enchantments
    "Ajani's Welcome": lambda: Card(
        "Ajani's Welcome", "Enchantment", cost={"W": 1, "B": 0, "C": 0},
        triggers=[{"event": "my_creature_etb", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Authority of the Consuls": lambda: Card(
        "Authority of the Consuls", "Enchantment", cost={"W": 1, "B": 0, "C": 0},
        triggers=[{"event": "opp_creature_etb", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Blind Obedience": lambda: Card(
        "Blind Obedience", "Enchantment", cost={"W": 1, "B": 0, "C": 1},
        triggers=[{"event": "my_plays_card", "action": sorin_life_gain_action, "params": {}}]
    ),
    "Cleric Class": lambda: Card(
        "Cleric Class", "Enchantment", cost={"W": 1, "B": 0, "C": 0},
        triggers=[{"event": "life_gained", "action": cleric_class_extra_life_action, "params": {}}]
    ),
    "Sanguine Bond": lambda: Card(
        "Sanguine Bond", "Enchantment", cost={"W": 0, "B": 1, "C": 4},
        triggers=[{"event": "life_gained", "action": lose_life_generic_action, "params": {"all_opponents": False}}]
    ),
    "The Meathook Massacre": lambda: Card(
        "The Meathook Massacre", "Sorcery", cost={"W": 0, "B": 1, "C": 2}
    ),

    # Instants and Sorceries (simplified - no triggers, just costs)
    "Anguished Unmaking": lambda: Card(
        "Anguished Unmaking", "Instant", cost={"W": 1, "B": 1, "C": 0}
    ),
    "Ascend from Avernus": lambda: Card(
        "Ascend from Avernus", "Sorcery", cost={"W": 1, "B": 0, "C": 1}
    ),
    "Damn": lambda: Card(
        "Damn", "Sorcery", cost={"W": 1, "B": 1, "C": 0}
    ),
    "Deadly Rollick": lambda: Card(
        "Deadly Rollick", "Instant", cost={"W": 0, "B": 0, "C": 0}
    ),
    "Flare of Fortitude": lambda: Card(
        "Flare of Fortitude", "Instant", cost={"W": 1, "B": 0, "C": 0}
    ),
    "Flawless Maneuver": lambda: Card(
        "Flawless Maneuver", "Instant", cost={"W": 1, "B": 0, "C": 2}
    ),
    "Path to Exile": lambda: Card(
        "Path to Exile", "Instant", cost={"W": 1, "B": 0, "C": 0}
    ),
    "Raise the Past": lambda: Card(
        "Raise the Past", "Sorcery", cost={"W": 0, "B": 0, "C": 3}
    ),
    "Rally the Ancestors": lambda: Card(
        "Rally the Ancestors", "Sorcery", cost={"W": 1, "B": 0, "C": 1}
    ),
    "Swords to Plowshares": lambda: Card(
        "Swords to Plowshares", "Instant", cost={"W": 1, "B": 0, "C": 0}
    ),
    "Teferi's Protection": lambda: Card(
        "Teferi's Protection", "Instant", cost={"W": 1, "B": 0, "C": 2}
    ),
    "Toxic Deluge": lambda: Card(
        "Toxic Deluge", "Sorcery", cost={"W": 0, "B": 1, "C": 2}
    ),

    # Planeswalkers
    "Sorin of House Markov": lambda: Card(
        "Sorin of House Markov", "Planeswalker", cost={"W": 0, "B": 1, "C": 2},
        triggers=[{"event": "my_plays_card", "action": sorin_life_gain_action, "params": {}}]
    ),

    # Special cases
    "Case of the Uneaten Feast": lambda: Card(
        "Case of the Uneaten Feast", "Enchantment", cost={"W": 1, "B": 0, "C": 0},
        triggers=[{"event": "my_creature_etb", "action": gain_life_action, "params": {"amount": 1}}]
    ),
    "Bolas's Citadel": lambda: Card(
        "Bolas's Citadel", "Artifact", cost={"W": 0, "B": 1, "C": 5},
        triggers=[]
    ),
}

def get_card(name):
    return CARD_DATABASE[name]() 