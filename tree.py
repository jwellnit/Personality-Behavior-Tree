#initial blackboard setup
blackboard = {};
blackboard["baseIdCount"] = 0;
blackboard["refIdCount"] = 0;

#node types
class Node:
    def __init__(self, baseId = -1, refId = -1):
        if (baseId == -1):
            self.baseId = blackboard["baseIdCount"]
            blackboard["baseIdCount"] += 1
        else:
            self.baseId = baseId
        if not "baseId::"+str(self.baseId) in blackboard:
            blackboard["baseId::"+str(self.baseId)] = {}
        self.refId = refId

    def referrence(self):
        refIdNew = blackboard["refIdCount"]
        blackboard["refIdCount"] += 1
        ref = Node(baseId = self.baseId, refId = refIdNew)
        return ref

    def excute(self):
        return "SUCCESS"

    def spec(self):
        print("Base ID: " + str(self.baseId) + "\n")
        print("Ref ID: " + str(self.refId) + "\n")



class ActionNode(Node):
    def __init__(self, effects, preconditions, baseId = -1, refId = -1, time = 1, effectText = "", involvedChars = [], consentingChars = []):
        Node.__init__(self, baseId, refId)
        self.effects = effects
        self.preconditions = preconditions
        self.time = time
        self.effectText = effectText
        self.involvedChars = involvedChars
        self.consentingChars = consentingChars

    def referrence(self):
        refIdNew = blackboard["refIdCount"]
        blackboard["refIdCount"] += 1
        ref = ActionNode(self.effects, self.preconditions, baseId = self.baseId, refId = refIdNew, time = self.time, effectText = self.effectText, involvedChars = self.involvedChars, consentingChars = self.consentingChars)
        return ref

    def execute(self):
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}

        if preconditions():
            effects()
            blackboard["displayText"] += self.effectText
            return "SUCCESS"
        else:
            blackboard["baseId::"+str(self.baseId)]["failures"] += 1
            return "FAILURE"

class CompositeNode(Node):
    def __init__(self, children, baseId = -1, refId = -1):
        Node.__init__(self, baseId, refId)
        self.children = children

    def referrence(self):
        refIdNew = blackboard["refIdCount"]
        blackboard["refIdCount"] += 1
        childRefs = []
        for c in self.children:
            childRef = c.referrence()
            childRefs.append(childRef);
        ref = CompositeNode(childRefs, baseId = self.baseId, refId = refIdNew)
        return ref

    def execute(self):
        for c in self.children:
            c.execute()
        return "SUCCESS"

    def spec(self):
        print("Base ID: " + str(self.baseId) + "\n")
        print("Ref ID: " + str(self.refId) + "\n")
        print("Children: [")
        for c in self.children:
            c.spec()
        print("]\n")

class SequenceNode(CompositeNode):
    def execute(self):
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}
            blackboard["refId::"+str(self.refId)]["currentIndex"] = 0;

        status = self.children[blackboard["refId::"+str(self.refId)]["currentIndex"]]

        if status == "SUCCESS":
            blackboard["refId::"+str(self.refId)]["currentIndex"] += 1
            if blackboard["refId::"+str(self.refId)]["currentIndex"] < len(self.children):
                return "RUNNING"
            else:
                blackboard["refId::"+str(self.refId)]["currentIndex"] += 0
                return "SUCCESS"
        elif status == "RUNNING":
            return "RUNNING"
        else:
            return "FAILURE"

class SelectorNode(CompositeNode):
    def execute(self):
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}
            blackboard["refId::"+str(self.refId)]["currentIndex"] = 0;

        status = self.children[blackboard["refId::"+str(self.refId)]["currentIndex"]]

        if status == "SUCCESS":
            return "SUCCESS"
        elif status == "RUNNING":
            return "RUNNING"
        else:
            blackboard["refId::"+str(self.refId)]["currentIndex"] += 1
            if blackboard["refId::"+str(self.refId)]["currentIndex"] < len(self.children):
                return "RUNNING"
            else:
                blackboard["refId::"+str(self.refId)]["currentIndex"] += 0
                return "FAILURE"

#variables
def setVariable(var, val):
    blackboard["variable::"+var] = val

def getVariable(var):
    if not "variable::"+var in blackboard:
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
    return treeRef

#execution
def turn():
    for t in agentTrees:
        setVariable("executingAgent", t[0])
        blackboard["displayText"] = ""
        t[1].execute()
        print("Effect Text: " + blackboard["displayText"])
