from tree import *

TOM_HOUSE = "TOM_HOUSE"
ALCH_HOUSE = "ALCH_HOUSE"
WOODS = "WOODS"

addPersonalityAgent("Tom", 0, 0, 0, 0, 0)
addPersonalityAgent("Alchemist", 0, 0, 0, 0, 0)

setVariable("herbsLocation", WOODS)
setVariable("coinLocation", "tom")
setVariable("potionLocation", "none")
setVariable("formulaLocation", ALCH_HOUSE)
setVariable("poisonLocation", ALCH_HOUSE)

setAgentVariable("Alchemist", "location", ALCH_HOUSE)
setVariable("sleep", False)
setVariable("poisonTicks", 0)
setVariable("knowHerbs", False)
setVariable("offer", False)
setVariable("cure", False)
setAgentVariable("Tom", "location", TOM_HOUSE)

def moveWoodsPrecond():
    return not getAgentVariable("$executingAgent$", "location") == WOODS

def moveWoodsEffects():
    setAgentVariable("$executingAgent$", "location", WOODS)

moveWoods = ActionNode(moveWoodsPrecond,
                    moveWoodsEffects,
                    effectText = "Move to the woods. ")

def moveAlchPrecond():
    return not getAgentVariable("$executingAgent$", "location") == ALCH_HOUSE

def moveAlchEffects():
    setAgentVariable("$executingAgent$", "location", ALCH_HOUSE)

moveAlch = ActionNode(moveAlchPrecond,
                    moveAlchEffects,
                    effectText = "Move to the Alchemist's house. ")

def moveTomPrecond():
    return not getAgentVariable("$executingAgent$", "location") == TOM_HOUSE

def moveTomEffects():
    setAgentVariable("$executingAgent$", "location", TOM_HOUSE)

moveTom = ActionNode(moveTomPrecond,
                    moveTomEffects,
                    effectText = "Move to Tom's house. ")

def waitPrecond():
    return True

def waitEffects():
    return

wait = ActionNode(waitPrecond,
                    waitEffects,
                    effectText = "Wait. ",
                    involvedChars = ["$executingAgent$"],
                    consentingChars = [])

def gatherHerbsPrecond():
    return getVariable("herbsLocation") == WOODS and getAgentVariable("$executingAgent$", "location") == WOODS

def gatherHerbsEffects():
    setVariable("herbsLocation", "$executingAgent$")

gatherHerbs = ActionNode(gatherHerbsPrecond,
                    gatherHerbsEffects,
                    effectText = "Gather herbs. ")

def tellHerbsPrecond():
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and not getVariable("playerSleep") and not getVariable("knowHerbs")

def tellHerbsEffects():
    setVariable("knowHerbs", True)

tellHerbs = ActionNode(tellHerbsPrecond,
                    tellHerbsEffects,
                    effectText = "Tell the Alchemist about the herbs. ")

def giveHerbsPrecond():
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and not getVariable("playerSleep") and getVariable("herbsLocation") == getVariable("executingAgent")

def giveHerbsEffects():
    setVariable("herbsLocation", "Alchemist")

giveHerbs = ActionNode(giveHerbsPrecond,
                    giveHerbsEffects,
                    effectText = "Give the herbs to the Alchemist. ")

def stealFormulaPrecond():
    return getAgentVariable("$executingAgent$", "location") == ALCH_HOUSE and (getAgentVariable("Alchemist", "location") != ALCH_HOUSE or getVariable("sleep")) and getVariable("formulaLocation") == ALCH_HOUSE

def stealFormulaEffects():
    setVariable("formulaLocation", "$executingAgent$")

stealFormula = ActionNode(stealFormulaPrecond,
                    stealFormulaEffects,
                    effectText = "Steal the formula. ")

def stealPoisonPrecond():
    return getAgentVariable("$executingAgent$", "location") == ALCH_HOUSE and (getAgentVariable("Alchemist", "location") != ALCH_HOUSE or getVariable("sleep")) and getVariable("poisonLocation") == ALCH_HOUSE

def stealPoisonEffects():
    setVariable("formulaLocation", "$executingAgent$")

stealPoison = ActionNode(stealPoisonPrecond,
                    stealPoisonEffects,
                    effectText = "Steal the poison. ")

def stealPotionPrecond():
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("sleep") and getVariable("potionLocation") == "Alchemist"

def stealPotionEffects():
    setVariable("potionLocation", "$executingAgent$")

stealPotion = ActionNode(stealPotionPrecond,
                    stealPotionEffects,
                    effectText = "Steal the potion. ")

def poisonAlchPrecond():
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("poisonLocation") == "$executingAgent$"

def poisonAlchEffects():
    setVariable("poisonLocation", "none")
    setVariable("poisonTicks", 5)

poisonAlch = ActionNode(poisonAlchPrecond,
                    poisonAlchEffects,
                    effectText = "Steal the potion. ")

def makePotionPrecond():
    return getVariable("formulaLocation") == "$executingAgent$" and getVariable("herbsLocation") == "$executingAgent$"

def makePotionEffects():
    setVariable("potionLocation", "$executingAgent$")
    setVariable("herbsLocation", "none")

makePotion = ActionNode(makePotionPrecond,
                    makePotionEffects,
                    effectText = "Make the potion. ")

def takePotionPrecond():
    return getVariable("potionLocation") == "$executingAgent$"

def takePotionEffects():
    setVariable("potionLocation", "none")
    setVariable("cure", True)

takePotion = ActionNode(takePotionPrecond,
                    takePotionEffects,
                    effectText = "Take the potion. ")

def makeOfferPrecond():
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("coinLocation") == "$executingAgent$" and getVariable("potionLocation") == "Alchemist"

def makeOfferEffects():
    setVariable("offer", True)

makeOffer = ActionNode(makeOfferPrecond,
                    makeOfferEffects,
                    effectText = "Offer to buy the potion. ")

#alchemist nodes
#sleep
def sleepPrecond():
    return True

def sleepEffects():
    setVariable("sleep", True)

sleep = ActionNode(sleepPrecond,
                    sleepEffects,
                    effectText = "Sleep. ")
#wake
def wakePrecond():
    return getVariable("sleep")

def wakeEffects():
    setVariable("sleep", False)

wake = ActionNode(wakePrecond,
                    wakeEffects,
                    effectText = "Sleep. ",
                    involvedChars = ["$executingAgent$"],
                    consentingChars = [])
#poisoned
def poisonedPrecond():
    return getVariable("poisonTicks") > 0

def poisonedEffects():
    setVariable("poisonTicks", getVariable("poisonTicks")-1)

poisoned = ActionNode(poisonedPrecond,
                    poisonedEffects,
                    effectText = "Be Poisoned. ")
#make
def makePotionAlchPrecond():
    return getVariable("herbsLocation") == "$executingAgent$"

def makePotionAlchEffects():
    setVariable("potionLocation", "$executingAgent$")
    setVariable("herbsLocation", "none")

makePotionAlch = ActionNode(makePotionAlchPrecond,
                    makePotionAlchEffects,
                    effectText = "Make the potion. ")
#acceptOffer
def acceptOfferPrecond():
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("offer")

def acceptOfferEffects():
    setVariable("offer", False)
    setVariable("potionLocation", "Tom")
    setVariable("coinLocation", "$executingAgent$")

acceptOffer = ActionNode(acceptOfferPrecond,
                    acceptOfferEffects,
                    effectText = "Sell the potion. ")

#tom tree
gatherSequence = SequenceUtilityNode([moveWoods, gatherHerbs])
tellAlchSequence = SequenceUtilityNode([moveAlch, tellHerbs])
giveAlchSequence = SequenceUtilityNode([moveAlch, giveHerbs])
poisonAlchSequence = SequenceUtilityNode([stealPoison, wait, poisonAlch])
makePotionSequence = SequenceUtilityNode([stealFormula,makePotion])
poisonLongSequence = SequenceUtilityNode([stealPoison, wait, wait, wait, poisonAlch])
letAlchWorkSequence = SequenceUtilityNode([wait, wait, wait, wait])
purchasePotionSequence = SequenceUtilityNode([makeOffer, wait])

#guards
def herbsTakenPrecond():
    return getVariable("herbsLocation") != getVariable("executingAgent") and not getVariable("knowHerbs")

herbsTaken1 = GuardNode(herbsTakenPrecond, gatherSequence)
herbsTaken2 = GuardNode(herbsTakenPrecond, tellAlchSequence)

def poisonUsedPrecond():
    return getVariable("poisonLocation") != "none"

poisonUsed1 = GuardNode(poisonUsedPrecond, poisonAlchSequence)
poisonUsed2 = GuardNode(poisonUsedPrecond, poisonLongSequence)

def potionMadePrecond():
    return getVariable("potionLocation") != "none"

potionMade1 = GuardNode(potionMadePrecond, purchasePotionSequence)
potionMade2 = GuardNode(potionMadePrecond, stealPotion)
potionMade3 = GuardNode(potionMadePrecond, makePotionSequence)

stealCraft = SequenceUtilityNode([herbsTaken1, poisonUsed1, potionMade3, takePotion])
stealAlch = SequenceUtilityNode([tellAlchSequence, poisonUsed2, potionMade2, takePotion])
purchase = SequenceUtilityNode([herbsTaken2, letAlchWorkSequence, potionMade1, takePotion])
purchaseCraft = SequenceUtilityNode([herbsTaken1, giveAlchSequence, letAlchWorkSequence, potionMade1, takePotion])

#Alchemist
alchHerbsSelect = SelectorUtilityNode([wait, gatherSequence])

def herbsTaken2Precond():
    return (getVariable("herbsLocation") != getVariable("executingAgent") or getVariable("herbsLocation") != "none") and getVariable("knowHerbs")

herbsAvail = GuardNode(herbsTaken2Precond, alchHerbsSelect)

alchPotionSelect = SelectorUtilityNode([wait, makePotionAlch])

def canMakePotionPrecond():
    return getVariable("herbsLocation") == getVariable("executingAgent") and getVariable("potionLocation") == "none"

canMakePotion = GuardNode(canMakePotionPrecond, alchPotionSelect)

offerSelect = SelectorUtilityNode([wait, acceptOffer])

def offerMadePrecond():
    return getVariable("potionLocation") == getVariable("executingAgent") and getVariable("offer")

offerMade = GuardNode(offerMadePrecond, offerSelect)

awakeSelector = SelectorUtilityNode([herbsAvail, canMakePotion, offerMade, sleep, wait])

def awakePrecond():
    return getVariable("poisonTicks") == 0 and not getVariable("sleep")

awake = GuardNode(awakePrecond, awakeSelector)

sleepSelector = SelectorUtilityNode([wait, wake])

def sleepGuardPrecond():
    return getVariable("poisonTicks") == 0 and getVariable("sleep")

sleepGuard= GuardNode(sleepGuardPrecond, sleepSelector)

def poisonGuardPrecond():
    return getVariable("poisonTicks") > 0

poisonGuard = GuardNode(poisonGuardPrecond, poisoned)

actions = SequenceNode([poisonGuard, sleepGuard, awake])

plans = SequenceUtilityNode([stealCraft, stealAlch, purchase, purchaseCraft])

tree1 = attachTreeToAgent("Tom", plans)
tree2 = attachTreeToAgent("Alchemist", actions)

turn()
inp = input("continue? (y/n): ")
quit = False
while (not quit):
    if inp == "y":
        turn()
        inp = input("continue? (y/n): ")
    elif inp == "n":
        quit = True
    else:
        print("not recognized\n")
        inp = input("continue? (y/n): ")
print("goodbye")

# print("Tom")
# tree1.spec()
# print("\n Alchemist")
# tree2.spec()
