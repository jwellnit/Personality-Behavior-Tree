#initial blackboard setup
blackboard = {};
blackboard["baseIdCount"] = 0;
blackboard["refIdCount"] = 0;

#node types
class Node:
    def __init__(self, baseId = -1, refId = -1):
        if (baseID == -1):
            this.baseId = blackboard["baseIdCount"]
            blackboard["baseIdCount"] += 1
        else:
            this.baseId = baseId
        if not blackboard["baseId::"+this.baseId]:
            blackboard["baseId::"+this.baseId] = {}
        this.refId = refId

    def referrence():
        refIdNew = blackboard["refIdCount"]
        blackboard["refIdCount"] += 1
        ref = Node(this.baseId, refIdNew)
        return ref

    def excute():
        return "SUCCESS"

class ActionNode(Node):
    def __init__(self, baseId, refId, effects, preconditions, time = 1, effectText = "", involvedChars = [], consentingChars = []):
        Node.__init__(baseId, refId)
        this.effects = effects
        this.preconditions = preconditions
        this.time = time
        this.effectText = effectText
        this.involvedChars = involvedChars
        this.consentingChars = consentingChars

    def referrence():
        refIdNew = blackboard["refIdCount"]
        blackboard["refIdCount"] += 1
        ref = ActionNode(this.baseId, refIdNew, this.effects, this.preconditions, this.time, this.effectText, this.involvedChars, this.consentingChars)
        return ref

    def execute():
        if not blackboard["refId::"+refId]:
            blackboard["refId::"+refId] = {}

        if preconditions():
            effects()
            blackboard["displayText"] += effectText
            return "SUCCESS"
        else:
            blackboard["baseId::"+this.baseId]["failures"] += 1
            return "FAILURE"

class CompositeNode(Node):
    def __init__(self, baseId, refId, children):
        Node.__init__(baseId, refId)
        this.children = children

    def referrence():
        refIdNew = blackboard["refIdCount"]
        blackboard["refIdCount"] += 1
        childRefs = []
        for c in children:
            childRef = c.referrence()
            childRefs.append(c);
        ref = ActionNode(this.baseId, refIdNew, this.effects, childRefs)
        return ref

    def execute():
        for c in children:
            c.execute()
        return "SUCCESS"

class SequenceNode(CompositeNode):
    def execute():
        if not blackboard["refId::"+refId]:
            blackboard["refId::"+refId] = {}
            blackboard["refId::"+refId]["currentIndex"] = 0;

        status = children[blackboard["refId::"+refId]["currentIndex"]]

        if status == "SUCCESS":
            blackboard["refId::"+refId]["currentIndex"] += 1
            if blackboard["refId::"+refId]["currentIndex"] < len(children):
                return "RUNNING"
            else:
                blackboard["refId::"+refId]["currentIndex"] += 0
                return "SUCCESS"
        elif status == "RUNNING":
            return "RUNNING"
        else:
            return "FAILURE"

class SelectorNode(CompositeNode):
    if not blackboard["refId::"+refId]:
        blackboard["refId::"+refId] = {}
        blackboard["refId::"+refId]["currentIndex"] = 0;

    status = children[blackboard["refId::"+refId]["currentIndex"]]

    if status == "SUCCESS":
        return "SUCCESS"
    elif status == "RUNNING":
        return "RUNNING"
    else:
        blackboard["refId::"+refId]["currentIndex"] += 1
        if blackboard["refId::"+refId]["currentIndex"] < len(children):
            return "RUNNING"
        else:
            blackboard["refId::"+refId]["currentIndex"] += 0
            return "FAILURE"

#variables
def setVariable(var, val):
    blackboard["variable::"+var] = val

def getVariable(var):
    if not blackboard["variable::"+var]:
        print("Variable " + var + " not set!")
        return
    return blackboard["variable::"+var]

#agents
agents = []
personality = {}

def addAgent(agent):
    agents.append(agent)

def addPersonalityAgent(agent, o, c, e, a, n):
    agents.append(agent)
    personality[agent] = {}
    personality[agent]["o"] = o
    personality[agent]["c"] = c
    personality[agent]["e"] = e
    personality[agent]["a"] = a
    personality[agent]["n"] = n

agentTrees = []

def attachTreeToAgent(agent, tree):
    treeRef = tree.referrence()
    agentTrees.append((agent, treeRef))

#execution
def turn():
    for t in agentTrees:
        setVariable("executingAgent", t[0])
        t[1].execute()
