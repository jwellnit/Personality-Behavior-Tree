from tree import *

TOWN = "TOWN"
ALCH_HOUSE = "ALCH_HOUSE"
COTTAGE = "COTTAGE"

addPersonalityAgent("Tom", 0, 0, 0, 0, -1)
addAgent("Alchemist")
addAgent("Guard")

setVariable("herbsLocation", COTTAGE)
setVariable("coinLocation", "Tom")
setVariable("potionLocation", "none")
setVariable("formulaLocation", ALCH_HOUSE)
setVariable("poisonLocation", ALCH_HOUSE)

setAgentVariable("Alchemist", "location", ALCH_HOUSE)
setAgentVariable("Guard", "location", TOWN)
setVariable("sleep", True)
setVariable("knock", False)
setVariable("drink", False)
setVariable("poisonTicks", 0)
setVariable("knowHerbs", False)
setVariable("offerHerbs", False)
setVariable("offerFormula", False)
setVariable("offerPotion", False)
setVariable("end", False)
setVariable("crime", False)
setVariable("guard", False)
setAgentVariable("Tom", "location", COTTAGE)

def moveCottagePrecond():
    # print("moveCottage")
    return not getAgentVariable("$executingAgent$", "location") == COTTAGE

def moveCottageEffects():
    setAgentVariable("$executingAgent$", "location", COTTAGE)

moveCottage = ActionNode(moveCottagePrecond,
                    moveCottageEffects,
                    effectText = "Move to the Cottage. ")

moveCottageGuard = GuardNode(moveCottagePrecond, moveCottage)
moveCottageSkip = SelectorNode([moveCottageGuard, wait])

def moveAlchPrecond():
    # print("moveAlch")
    return not getAgentVariable("$executingAgent$", "location") == ALCH_HOUSE

def moveAlchEffects():
    setAgentVariable("$executingAgent$", "location", ALCH_HOUSE)

moveAlch = ActionNode(moveAlchPrecond,
                    moveAlchEffects,
                    effectText = "Move to the Alchemist's house. ")

moveAlchGuard = GuardNode(moveAlchPrecond, moveAlch)
moveAlchSkip = SelectorNode([moveAlchGuard, wait])

def knockAlchPrecond():
    # print("knockAlch")
    return (getAgentVariable("$executingAgent$", "location") == TOWN and getAgentVariable("Alchemist", "location") == ALCH_HOUSE)

def knockAlchEffects():
    setVariable("sleep", False)
    setVariable("knock", True)

knockAlch = ActionNode(knockAlchPrecond,
                    knockAlchEffects,
                    effectText = "Tom knocks on the Alchemist's door. ",
                    involvedChars = ["$executingAgent$", "Alchemist"],
                    consentingChars = ["$executingAgent$"])

def knockAlchGuardPrecond():
    return getAgentVariable("$executingAgent$", "location") != ALCH_HOUSE

knockAlchGuard = GuardNode(knockAlchGuardPrecond, knockAlch)
knockAlchSkip = SelectorNode([knockAlchGuard, wait])

def breakInAlchPrecond():
    # print("breakInAlch")
    rand = random.random()
    ret = getAgentVariable("$executingAgent$", "location") == TOWN and (getAgentVariable("Alchemist", "location") != ALCH_HOUSE or getVariable("poisonTicks") > 0 or (getVariable("sleep") and rand >= .5))
    if (not ret):
        setAgentVariable("$executingAgent$", "location", ALCH_HOUSE)
        setVariable("crime", True)
        print("Tom is caught Breaking into the Alchemist's house. ")

    return ret

def breakInAlchEffects():
    setAgentVariable("$executingAgent$", "location", ALCH_HOUSE)

breakInAlch = ActionNode(breakInAlchPrecond,
                    breakInAlchEffects,
                    effectText = "Breaks in to the Alchemist's house. ",
                    involvedChars = ["$executingAgent$", "Alchemist"],
                    consentingChars = ["$executingAgent$"])

def breakInAlchGuardPrecond():
    return getAgentVariable("$executingAgent$", "location") != ALCH_HOUSE

breakInAlchGuard = GuardNode(breakInAlchGuardPrecond, breakInAlch)
breakInAlchSkip = SelectorNode([breakInAlchGuard, wait])

def answerKnockAlchPrecond():
    return getVariable("knock") and (not getVariable("sleep")) and getVariable("poisonTicks") <= 0 and getAgentVariable("Alchemist", "location") == ALCH_HOUSE

def answerKnockAlchEffects():
    setAgentVariable("Tom", "location", ALCH_HOUSE)
    setVariable("knock", False)

answerKnock = ActionNode(answerKnockAlchPrecond,
                    answerKnockAlchEffects,
                    effectText = "The Alchemist answers the door and lets Tom in. ",
                    involvedChars = ["Tom", "Alchemist"],
                    consentingChars = ["Alchemist", "Tom"])

def moveTownPrecond():
    # print("moveTown")
    return not getAgentVariable("$executingAgent$", "location") == TOWN

def moveTownEffects():
    setAgentVariable("$executingAgent$", "location", TOWN)

moveTown = ActionNode(moveTownPrecond,
                    moveTownEffects,
                    effectText = "Move to the Town. ")

moveTownGuard = GuardNode(moveTownPrecond, moveTown)
moveTownSkip = SelectorNode([moveTownGuard, wait])

def waitPrecond():
    # print("wait")
    return True

def waitEffects():
    return

wait = ActionNode(waitPrecond,
                    waitEffects,
                    effectText = "Wait. ",
                    involvedChars = ["$executingAgent$"],
                    consentingChars = [])

def gatherHerbsPrecond():
    # print("gatherHerbs")
    return getVariable("herbsLocation") == COTTAGE and getAgentVariable("$executingAgent$", "location") == COTTAGE

def gatherHerbsEffects():
    setVariable("herbsLocation", "$executingAgent$")

gatherHerbs = ActionNode(gatherHerbsPrecond,
                    gatherHerbsEffects,
                    effectText = "Gather herbs. ")
def gatherHerbsGuardPrecond():
    return getVariable("herbsLocation") != "$executingAgent$" and getAgentVariable("$executingAgent$", "location") == COTTAGE

gatherHerbsGuard = GuardNode(gatherHerbsGuardPrecond, gatherHerbs)
gatherHerbsSkip = SelectorNode([gatherHerbsGuard, wait])

def makePoisonPrecond():
    # print("makePoison")
    return getAgentVariable("$executingAgent$", "location") == COTTAGE

def makePoisonEffects():
    setVariable("poisonLocation", "$executingAgent$")

makePoison = ActionNode(makePoisonPrecond,
                    makePoisonEffects,
                    effectText = "Gather poisonous herbs and make poison. ")

def makePoisonGuardPrecond():
    return getAgentVariable("$executingAgent$", "location") == COTTAGE

makePoisonGuard = GuardNode(makePoisonGuardPrecond, makePoison)
makePoisonSkip = SelectorNode([makePoisonGuard, wait])

def tellHerbsPrecond():
    # print("tellHerbs")
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and (not getVariable("sleep")) and (not getVariable("knowHerbs"))

def tellHerbsEffects():
    setVariable("knowHerbs", True)

tellHerbs = ActionNode(tellHerbsPrecond,
                    tellHerbsEffects,
                    effectText = "Tell the Alchemist about the herbs. ")

tellHerbsGuard = GuardNode(tellHerbsPrecond, tellHerbs)
tellHerbsSkip = SelectorNode([tellHerbsGuard, wait])

def giveHerbsPrecond():
    # print("giveHerbs")
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and not getVariable("sleep") and getVariable("herbsLocation") == getVariable("executingAgent")

def giveHerbsEffects():
    setVariable("herbsLocation", "Alchemist")

giveHerbs = ActionNode(giveHerbsPrecond,
                    giveHerbsEffects,
                    effectText = "Give the herbs to the Alchemist. ")

giveHerbsGuard = GuardNode(giveHerbsPrecond, giveHerbs)
giveHerbsSkip = SelectorNode([giveHerbsGuard, wait])

def stealFormulaPrecond():
    # print("stealFormula")
    rand = random.random()
    ret = getAgentVariable("$executingAgent$", "location") == ALCH_HOUSE and (getAgentVariable("Alchemist", "location") != ALCH_HOUSE or getVariable("poisonTicks") > 0 or getVariable("sleep") or rand >= .5) and getVariable("formulaLocation") == ALCH_HOUSE
    if (not ret):
        setVariable("crime", True)
        print("Tom is caught stealing the formula. ")
    return ret

def stealFormulaEffects():
    setVariable("formulaLocation", "$executingAgent$")

stealFormula = ActionNode(stealFormulaPrecond,
                    stealFormulaEffects,
                    effectText = "Steal the formula. ",
                    involvedChars = ["$executingAgent$", "Alchemist"],
                    consentingChars = ["$executingAgent$"])

def stealFormulaGuardPrecond():
    ret = getAgentVariable("$executingAgent$", "location") == ALCH_HOUSE and getVariable("formulaLocation") == ALCH_HOUSE
    return ret

stealFormulaGuard = GuardNode(stealFormulaGuardPrecond, stealFormula)
stealFormulaSkip = SelectorNode([stealFormulaGuard, wait])

def stealHerbsPrecond():
    # print("stealHerbs")
    rand = random.random()
    ret = getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and (getVariable("poisonTicks") > 0 or getVariable("sleep") or rand >= .5) and getVariable("herbsLocation") == "Alchemist"
    if (not ret):
        setVariable("crime", True)
        print("Tom is caught stealing the herbs. ")
    return ret

def stealHerbsEffects():
    setVariable("herbsLocation", "$executingAgent$")

stealHerbs = ActionNode(stealHerbsPrecond,
                    stealHerbsEffects,
                    effectText = "Steal the herbs. ",
                    involvedChars = ["$executingAgent$", "Alchemist"],
                    consentingChars = ["$executingAgent$"])

def stealHerbsGuardPrecond():
    ret = getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("herbsLocation") == "Alchemist"
    return ret

stealHerbsGuard = GuardNode(stealHerbsGuardPrecond, stealHerbs)
stealHerbsSkip = SelectorNode([stealHerbsGuard, wait])

def stealPotionPrecond():
    # print("stealPotion")
    rand = random.random()
    ret = getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and (getVariable("poisonTicks") > 0 or getVariable("sleep") or rand >= .5) and getVariable("potionLocation") == "Alchemist"
    if (not ret):
        setVariable("crime", True)
        print("Tom is caught stealing the potion. ")
    return ret

def stealPotionEffects():
    setVariable("potionLocation", "$executingAgent$")

stealPotion = ActionNode(stealPotionPrecond,
                    stealPotionEffects,
                    effectText = "Steal the potion. ",
                    involvedChars = ["$executingAgent$", "Alchemist"],
                    consentingChars = ["$executingAgent$"])

def stealPotionGuardPrecond():
    ret = getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("potionLocation") == "Alchemist"
    return ret

stealPotionGuard = GuardNode(stealPotionGuardPrecond, stealPotion)
stealPotionSkip = SelectorNode([stealPotionGuard, wait])

def poisonAlchPrecond():
    # print("poisonAlch")
    rand = random.random()
    ret = getAgentVariable("$executingAgent$", "location") == ALCH_HOUSE and (getAgentVariable("Alchemist", "location") != ALCH_HOUSE or getVariable("poisonTicks") > 0 or getVariable("sleep") or rand >= .5) and getVariable("poisonLocation") == "$executingAgent$"
    if (not ret):
        setVariable("crime", True)
        print("Tom is caught poisoning the Alchemist. ")
    return ret

def poisonAlchEffects():
    setVariable("poisonLocation", "none")
    setVariable("drink", True)

poisonAlch = ActionNode(poisonAlchPrecond,
                    poisonAlchEffects,
                    effectText = "Poison the Alchemist's drink. ",
                    involvedChars = ["$executingAgent$", "Alchemist"],
                    consentingChars = ["$executingAgent$"])

def poisonAlchGuardPrecond():
    ret = getAgentVariable("$executingAgent$", "location") == ALCH_HOUSE and getVariable("drink") and getVariable("poisonTicks") <= 0 and getVariable("poisonLocation") == "$executingAgent$"
    return ret

poisonAlchGuard = GuardNode(poisonAlchGuardPrecond, poisonAlch)
poisonAlchSkip = SelectorNode([poisonAlchGuard, wait])

def makePotionPrecond():
    # print("makePotion")
    return getVariable("formulaLocation") == "$executingAgent$" and getVariable("herbsLocation") == "$executingAgent$"

def makePotionEffects():
    setVariable("potionLocation", "$executingAgent$")
    setVariable("herbsLocation", "none")

makePotion = ActionNode(makePotionPrecond,
                    makePotionEffects,
                    effectText = "Make the potion. ")

makePotionGuard = GuardNode(makePotionPrecond, makePotion)
makePotionSkip = SelectorNode([makePotionGuard, wait])

def takePotionPrecond():
    # print("takePotion")
    return getVariable("potionLocation") == getVariable("executingAgent")

def takePotionEffects():
    setVariable("potionLocation", "none")
    setVariable("end", True)

takePotion = ActionNode(takePotionPrecond,
                    takePotionEffects,
                    effectText = "Take the potion. ")

def makeOfferHerbsPrecond():
    # print("makeOfferHerbs")
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("coinLocation") == getVariable("executingAgent") and getVariable("herbsLocation") == "Alchemist"

def makeOfferHerbsEffects():
    setVariable("offerHerbs", True)

makeOfferHerbs = ActionNode(makeOfferHerbsPrecond,
                    makeOfferHerbsEffects,
                    effectText = "Offer to buy the herbs. ")

makeOfferHerbsGuard = GuardNode(makeOfferHerbsPrecond, makeOfferHerbs)
makeOfferHerbsSkip = SelectorNode([makeOfferHerbsGuard, wait])

def makeOfferFormulaPrecond():
    # print("makeOfferFormula")
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("coinLocation") == getVariable("executingAgent") and getVariable("formulaLocation") == "Alchemist"

def makeOfferFormulaEffects():
    setVariable("offerFormula", True)

makeOfferFormula = ActionNode(makeOfferFormulaPrecond,
                    makeOfferFormulaEffects,
                    effectText = "Offer to buy the potion formula. ")

makeOfferFormulaGuard = GuardNode(makeOfferFormulaPrecond, makeOfferFormula)
makeOfferFormulaSkip = SelectorNode([makeOfferFormulaGuard, wait])

def makeOfferPotionPrecond():
    # print("makeOfferPotion")
    # print(getAgentVariable("$executingAgent$", "location"))
    # print(getAgentVariable("Alchemist", "location"))
    # print(getVariable("coinLocation"))
    # print(getVariable("executingAgent"))
    # print(getVariable("potionLocation"))
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("coinLocation") == getVariable("executingAgent") and getVariable("potionLocation") == "Alchemist"

def makeOfferPotionEffects():
    setVariable("offerPotion", True)

makeOfferPotion = ActionNode(makeOfferPotionPrecond,
                    makeOfferPotionEffects,
                    effectText = "Offer to buy the potion. ")

makeOfferPotionGuard = GuardNode(makeOfferPotionPrecond, makeOfferPotion)
makeOfferPotionSkip = SelectorNode([makeOfferPotionGuard, wait])

#alchemist nodes
#sleep
def sleepPrecond():
    getVariable("sleep")

def sleepEffects():
    return

sleep = ActionNode(sleepPrecond,
                    sleepEffects,
                    effectText = "The Alchemist remains asleep. ")
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

#get poisoned
def getPoisonedPrecond():
    return getVariable("drink") and (not getVariable("sleep")) and (getVariable("poisonTicks") <= 0) and getAgentVariable("$executingAgent$", "location") == ALCH_HOUSE

def getPoisonedEffects():
    setVariable("poisonTicks", 5)

getPoisoned = ActionNode(getPoisonedPrecond,
                    getPoisonedEffects,
                    effectText = "Unknowingly, the alchemist drinks the poison and faints. ")

#poisoned
def poisonedPrecond():
    return getVariable("poisonTicks") > 0

def poisonedEffects():
    setVariable("poisonTicks", getVariable("poisonTicks")-1)

poisoned = ActionNode(poisonedPrecond,
                    poisonedEffects,
                    effectText = "Be Poisoned. ")
#make
def gatherHerbsAlchPrecond():
    ret = getVariable("herbsLocation") == COTTAGE and getAgentVariable("$executingAgent$", "location") == COTTAGE
    if getVariable("herbsLocation") != COTTAGE and getAgentVariable("$executingAgent$", "location") == COTTAGE:
        setVariable("knowHerbs", False)
    return ret

def gatherHerbsAlchEffects():
    setVariable("herbsLocation", "$executingAgent$")
    setVariable("knowHerbs", False)

gatherHerbsAlch = ActionNode(gatherHerbsAlchPrecond,
                    gatherHerbsAlchEffects,
                    effectText = "Gather herbs. ")

def makePotionAlchPrecond():
    return getVariable("herbsLocation") == "Alchemist"  and (not getVariable("sleep")) and (getVariable("poisonTicks") <= 0)

def makePotionAlchEffects():
    setVariable("potionLocation", "Alchemist")
    setVariable("herbsLocation", "none")

makePotionAlch = ActionNode(makePotionAlchPrecond,
                    makePotionAlchEffects,
                    effectText = "Make the potion. ")
#acceptOffer
def acceptOfferHerbsPrecond():
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("offerHerbs")  and (not getVariable("sleep")) and (getVariable("poisonTicks") <= 0)

def acceptOfferHerbsEffects():
    setVariable("offerHerbs", False)
    setVariable("herbsLocation", "Tom")
    setVariable("coinLocation", "$executingAgent$")

acceptOfferHerbs = ActionNode(acceptOfferHerbsPrecond,
                    acceptOfferHerbsEffects,
                    effectText = "Sell the herbs. ")

def acceptOfferFormulaPrecond():
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("offerFormula")  and (not getVariable("sleep")) and (getVariable("poisonTicks") <= 0)

def acceptOfferFormulaEffects():
    setVariable("offerFormula", False)
    setVariable("formulaLocation", "Tom")
    setVariable("coinLocation", "$executingAgent$")

acceptOfferFormula = ActionNode(acceptOfferFormulaPrecond,
                    acceptOfferFormulaEffects,
                    effectText = "Sell the Recipie. ")

def acceptOfferPotionPrecond():
    return getAgentVariable("$executingAgent$", "location") == getAgentVariable("Alchemist", "location") and getVariable("offerPotion")  and (not getVariable("sleep")) and (getVariable("poisonTicks") <= 0)

def acceptOfferPotionEffects():
    setVariable("offerPotion", False)
    setVariable("potionLocation", "Tom")
    setVariable("coinLocation", "$executingAgent$")

acceptOfferPotion = ActionNode(acceptOfferPotionPrecond,
                    acceptOfferPotionEffects,
                    effectText = "Sell the potion. ")

def callGuardPrecond():
    return getVariable("crime") and (not getVariable("sleep")) and (getVariable("poisonTicks") <= 0)

def callGuardEffects():
    setVariable("crime", False)
    setVariable("guard", True)

callGuard = ActionNode(callGuardPrecond,
                    callGuardEffects,
                    effectText = "Call the guards. ")

def pursuePrecond():
    return getVariable("guard") and not getAgentVariable("$executingAgent$", "location") == getAgentVariable("Tom", "location")

def pursueEffects():
    setAgentVariable("$executingAgent$", "location", getAgentVariable("Tom", "location"))

pursue = ActionNode(pursuePrecond,
                    pursueEffects,
                    effectText = "Pursue Tom. ")

def arrestPrecond():
    return getVariable("guard") and getAgentVariable("$executingAgent$", "location") == getAgentVariable("Tom", "location")

def arrestEffects():
    setVariable("guard", False)
    setVariable("end", True)

arrest = ActionNode(arrestPrecond,
                    arrestEffects,
                    effectText = "Arrest Tom. ")

def gameOverPrecond():
    return getVariable("end")

def gameOverEffects():
    return

gameOver = ActionNode(gameOverPrecond,
                    gameOverEffects,
                    effectText = "Game Over. ")

#tom tree
# plan1 = SequenceUtilityNode([gatherHerbsSkip, moveTownSkip, knockAlch, tellHerbsSkip, stealFormulaSkip, makePotionSkip, takePotion])
# plan2 = SequenceUtilityNode([makePoisonSkip, gatherHerbsSkip, moveTownSkip, knockAlchSkip, poisonAlchSkip, stealFormulaSkip, makePotionSkip, takePotion])
# plan3 = SequenceUtilityNode([gatherHerbsSkip, moveTownSkip, breakInAlchSkip, stealFormulaSkip, makePotionSkip, takePotion])
# plan4 = SequenceUtilityNode([gatherHerbsSkip, moveTownSkip, knockAlch, giveHerbsSkip, wait, stealPotionSkip, takePotion])
# plan5 = SequenceUtilityNode([gatherHerbsSkip, moveTownSkip, knockAlch, giveHerbsSkip, wait, makeOfferPotionSkip, wait, takePotion])
# plan6 = SequenceUtilityNode([makePoisonSkip, gatherHerbsSkip, moveTownSkip, knockAlch, giveHerbsSkip, poisonAlchSkip, stealPotionSkip, takePotion])
# plan7 = SequenceUtilityNode([moveTownSkip, knockAlchSkip, tellHerbsSkip, wait, wait, wait, makeOfferPotionSkip, wait, takePotion])
# plan8 = SequenceUtilityNode([makePoisonSkip, moveTownSkip, knockAlchSkip, tellHerbsSkip, poisonAlchSkip, wait, stealPotionSkip, takePotion])
# plan9 = SequenceUtilityNode([moveTownSkip, knockAlchSkip, tellHerbsSkip, stealFormulaSkip, wait, stealHerbsSkip, makePotionSkip, takePotion])
# plan10 = SequenceUtilityNode([makePoisonSkip, moveTownSkip, knockAlchSkip, tellHerbsSkip, poisonAlchSkip, wait, wait, stealFormulaSkip, stealHerbsSkip, makePotionSkip, takePotion])
# plan11 = SequenceUtilityNode([gatherHerbsSkip, moveTownSkip, knockAlch, makeOfferFormulaSkip, wait, makePotionSkip, takePotion])

plan1 = SequenceUtilityNode([gatherHerbs, moveTownSkip, knockAlch, tellHerbs, stealFormula, makePotion, takePotion], printOut = "plan 1")
plan2 = SequenceUtilityNode([makePoison, gatherHerbs, moveTownSkip, knockAlch, poisonAlch, stealFormula, makePotion, takePotion], printOut = "plan 2")
plan3 = SequenceUtilityNode([gatherHerbs, moveTownSkip, breakInAlch, stealFormula, makePotion, takePotion], printOut = "plan 3")
plan4 = SequenceUtilityNode([gatherHerbs, moveTownSkip, knockAlch, giveHerbs, wait, stealPotion, takePotion], printOut = "plan 4")
plan5 = SequenceUtilityNode([gatherHerbs, moveTownSkip, knockAlch, giveHerbs, wait, makeOfferPotion, wait, takePotion], printOut = "plan 5")
plan6 = SequenceUtilityNode([makePoison, gatherHerbs, moveTownSkip, knockAlch, giveHerbs, poisonAlch, stealPotion, takePotion], printOut = "plan 6")
plan7 = SequenceUtilityNode([moveTownSkip, knockAlch, tellHerbs, wait, wait, wait, makeOfferPotion, wait, takePotion], printOut = "plan 7")
plan8 = SequenceUtilityNode([makePoison, moveTownSkip, knockAlch, tellHerbs, poisonAlch, wait, stealPotion, takePotion], printOut = "plan 8")
plan9 = SequenceUtilityNode([moveTownSkip, knockAlch, tellHerbs, stealFormula, wait, stealHerbs, makePotion, takePotion], printOut = "plan 9")
plan10 = SequenceUtilityNode([makePoison, moveTownSkip, knockAlch, tellHerbs, poisonAlch, wait, wait, stealFormula, stealHerbs, makePotion, takePotion], printOut = "plan 10")
plan11 = SequenceUtilityNode([gatherHerbs, moveTownSkip, knockAlch, makeOfferFormula, wait, makePotion, takePotion], printOut = "plan 11")

#Alchemist
gatherSequence2 = SequenceUtilityNode([moveCottage, gatherHerbsAlch])

def herbsTaken2Precond():
    return getVariable("herbsLocation") != getVariable("executingAgent") and getVariable("knowHerbs")

herbsAvail = GuardNode(herbsTaken2Precond, gatherSequence2)

def notHomePrecond():
    return getAgentVariable("Alchemist", "location") != ALCH_HOUSE

notHome = GuardNode(notHomePrecond, moveAlch)

awakeSelector = SelectorNode([herbsAvail, notHome, callGuard, answerKnock, acceptOfferPotion, acceptOfferHerbs, acceptOfferFormula, makePotionAlch, getPoisoned, wait])

def awakePrecond():
    return getVariable("poisonTicks") == 0 and not getVariable("sleep")

awake = GuardNode(awakePrecond, awakeSelector)

def sleepGuardPrecond():
    return getVariable("poisonTicks") == 0 and getVariable("sleep")

sleepGuard = GuardNode(sleepGuardPrecond, sleep)

def poisonGuardPrecond():
    return getVariable("poisonTicks") > 0

poisonGuard = GuardNode(poisonGuardPrecond, poisoned)

arrestSelect = SelectorNode([pursue, arrest])

def arrestGuardPrecond():
    return getVariable("guard")

arrestGuard = GuardNode(arrestGuardPrecond, arrestSelect)

patrolSelect = SelectorNode([arrestGuard, wait])

guardTree = SelectorNode([gameOver, patrolSelect])

actions = SelectorNode([poisonGuard, sleepGuard, awake])

alchTree = SelectorNode([gameOver, actions])

plans = SelectorUtilityNode([plan1, plan2, plan3, plan4, plan5, plan6, plan7, plan8, plan9, plan10, plan11])

tomTree = SelectorNode([gameOver, plans])

tree1 = attachTreeToAgent("Tom", tomTree)
tree2 = attachTreeToAgent("Alchemist", alchTree)
tree3 = attachTreeToAgent("Guard", guardTree)

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
