import sys
sys.path.append('.')
from desc_dict import DESC_ZH

lines = """Place a fire trap that explodes when an enemy approaches, causing ${$RAP*0.1+$27026m1} to ${$RAP*0.1+$27026M1} Fire damage and burning all enemies for $27026o2 additional Fire damage over $27026d to all within $27026a1 yards.  Trap will exist for $27025d.  Only one trap can be active at a time.
Allows a physician to make and use bandages up to a potential skill of 375.   The cloth used to make those bandages are found on humanoids in the world.
Your pet growls at the target, generating threat and increasing the likelihood the target will attack it.
A stinging shot that puts the target to sleep for $d.  Any damage will cancel the effect.  When the target wakes up, the Sting causes $27069o1 Nature damage over $27069d.  Only one Sting per Hunter can be active on the target at a time.
Launches Arcane Missiles at the enemy, causing $27076s1 Arcane damage every $t2 sec for $d.
Launches Arcane Missiles at the enemy, causing $27076s1 Arcane damage every $27075t2 sec for $27075d.
Ice shards pelt the target area doing ${$42198m1*8} Frost damage over $d.
Conjures $s1 $lskin:skin; of glacier water, providing the mage and $ghis:her; allies with something to drink.\n\nConjured items disappear if logged out for more than 15 minutes.
Conjures a mana emerald that can be used to instantly restore $27103s1 mana.  3 charges.\n\nConjured items disappear if logged out for more than 15 minutes.
Infuses the target's party with brilliance, increasing their Intellect by $s1 for $d.
Fills the Paladin with the spirit of a crusader for $d, granting $s1 melee attack power.  The Paladin also attacks $s2% faster, but deals less damage with each attack.  Only one Seal can be active on the Paladin at any one time.\n\nUnleashing this Seal's energy will judge an enemy for $27159d, increasing Holy damage taken by up to $27159s1.  Your melee strikes will refresh the spell's duration.  Only one Judgement per Paladin can be active at any one time.
Blasts the target with Holy energy, causing $27176s1 Holy damage to an enemy, or $27175s1 healing to an ally.
Calls down a fiery rain to burn enemies in the area of effect for ${$42218m1*4} Fire damage over $d.
Ignites the area surrounding the caster, causing $s2 Fire damage to $ghimself:herself; and $27214s1 Fire damage to all nearby enemies every $t2 sec.  Lasts $d.
Drains the soul of the target, causing $o2 Shadow damage over $d.  If the target dies while being drained, and yields experience or honor, the caster gains a Soul Shard.  Soul Shards are required for other spells.
Curses the target with agony, causing $o1 Shadow damage over $d.  This damage is dealt slowly at first, and builds up as the Curse reaches its full duration.  Only one Curse per Warlock can be active on any one target.
Curses the target for $d, reducing Arcane, Fire, Frost, and Shadow resistances by $s1 and increasing Arcane, Fire,  Frost, and Shadow damage taken by $s2%.  Only one Curse per Warlock can be active on any one target.
Creates a Master Healthstone that can be used to instantly restore $27235s1 health.\n\nConjured items disappear if logged out for more than 15 minutes.
Creates a Master Soulstone.  The Soulstone can be used to store one target's soul.  If the target dies while their soul is stored, they will be able to resurrect with $27240s1 health and $27240q1 mana.\n\nConjured items disappear if logged out for more than 15 minutes.
Right Click to summon and dismiss Gurky the baby murloc.
Imbeds a demon seed in the enemy target, causing $o1 Shadow damage over $d.  When the target takes $s2 total damage or dies, the seed will inflict $27285s1 Shadow damage to all other enemies within $27285a1 yards of the target.  Only one Corruption spell per Warlock can be active on any one target.
Creates a Master Firestone which can be equipped.  When equipped, enchants the main hand weapon with fire, granting each attack a chance to deal $27253s1 additional Fire damage.  In addition, equipping the Master Firestone increases the damage done by fire spells by $27256s1.\n\nConjured items disappear if logged out for more than 15 minutes.
Transfers $s1 health from the target to the caster every $t1 sec.  Lasts $d.
Surrounds the target in a shield of fire, increasing Fire resistance by $s2 and making every strike against the target cause $s1 Fire damage to the attacker.  Lasts $d.  The caster cannot cast Fire Shield on himself.
Taunts the creature, increasing the chance that it will attack the Voidwalker.  More effective than Torment (Rank 6).
Taunts all enemies within $a1 yards, increasing the chance that they will attack the Voidwalker and reducing chance to hit by $s2% for $d.  More effective than Suffering (Rank 4).
The Voidwalker consumes nearby shadows to bolster its form, recovering $o1 health over $d and greatly increasing stealth detection to all nearby friendly targets within $54501a yards. Cannot be used while in combat.
An instant attack that lashes the target, causing $s1 Shadow damage.
Soothes the target, increasing the chance that it will attack something else and decreases melee attack speed by $s2% for $d.  More effective than Soothing Kiss (Rank 4).
Purges $s1 harmful magic $leffect:effects; from a friend or $s1 beneficial magic $leffect:effects; from an enemy.  If an effect is devoured, the Felhunter will be healed for $27278s1.
Purges $27277s1 harmful magic $leffect:effects; from a friend or $27277s1 beneficial magic $leffect:effects; from an enemy.  If an effect is devoured, the Felhunter will be healed for $s2.
Imbeds a demon seed in the enemy target, causing $27243o1 Shadow damage over $27243d.  When the target takes $27243s2 total damage or dies, the seed will inflict $27285s1 Shadow damage to all enemies within $27285a1 yards of the target.  Only one Corruption spell per Warlock can be active on any one target.
Ambush the target, causing $s2% weapon damage plus 335 to the target.  Must be stealthed and behind the target.  Requires a dagger in the main hand.  Awards $s3 combo $lpoint:points;.
Right Click to summon and dismiss Kwee Q. Peddlefeet.
An aimed shot that increases ranged damage by $s1.
Power infuses your raid or party members, increasing their Spirit by $s1 for $d.
Power infuses your raid or party members, increasing their Shadow resistance by $s1 for $d.
Increases the range of your Smite and Holy Fire spells and the radius of your Prayer of Healing, Holy Nova and Circle of Healing spells by $s1%.
Causes an explosion of holy light around the caster, causing $s1 Holy damage to all enemy targets within $a1 yards and healing all party members within $27803a1 yards for $27803s1.  These effects cause no threat.
Causes an explosion of holy light around the caster, causing $s1 Holy damage to all enemy targets within $a1 yards and healing all party members within $27804a1 yards for $27804s1.  These effects cause no threat.
Causes an explosion of holy light around the caster, causing $s1 Holy damage to all enemy targets within $a1 yards and healing all party members within $27805a1 yards for $27805s1.  These effects cause no threat.
Causes an explosion of holy light around the caster, causing $27799s1 Holy damage to all enemy targets within $27799a1 yards and healing all party members within $27803a1 yards for $27803s1.  These effects cause no threat.
Causes an explosion of holy light around the caster, causing $27800s1 Holy damage to all enemy targets within $27800a1 yards and healing all party members within $27804a1 yards for $27804s1.  These effects cause no threat.
Causes an explosion of holy light around the caster, causing $27801s1 Holy damage to all enemy targets within $27801a1 yards and healing all party members within $27805a1 yards for $27805s1.  These effects cause no threat.
After being struck by a melee or ranged critical hit, heal $s1% of the damage taken over $27813d.
Heals the target over $d.
After being struck by a melee or ranged critical hit, heal $s1% of the damage taken over $27817d.""".split("\n")

for line in lines:
    line = line.strip()
    if not line: continue
    if line not in DESC_ZH:
        print(f"MISSING: {line}")
    else:
        print(f"EXISTS: {line[:30]}...")
