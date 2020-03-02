from dill.source import getsource

#initial blackboard setup
blackboard = {};
blackboard["baseIdCount"] = 0;
blackboard["refIdCount"] = 0;

#node types
#parent node, never used directly
class Node:
    def __init__(self, baseId = -1, refId = -1):
        #assign a baseID
        if (baseId == -1):
            self.baseId = blackboard["baseIdCount"]
            blackboard["baseIdCount"] += 1
        else:
            self.baseId = baseId

        #create an entry for this node type in the blackboard
        if not "baseId::"+str(self.baseId) in blackboard:
            blackboard["baseId::"+str(self.baseId)] = {}
            blackboard["baseId::"+str(self.baseId)]["failures"] = 0
            blackboard["baseId::"+str(self.baseId)]["attempts"] = 0

        self.refId = refId

    #create a deep copy of the node
    def referrence(self):
        refIdNew = blackboard["refIdCount"] #new refID
        blackboard["refIdCount"] += 1
        ref = Node(baseId = self.baseId, refId = refIdNew)
        return ref

    #execute the node
    def excute(self):
        return "SUCCESS"

    #print out identifying informaation
    def spec(self):
        print("Base ID: " + str(self.baseId) + "\n")
        print("Ref ID: " + str(self.refId) + "\n")

    #utility calc, base, never called
    def utility(self):
        utility = 0
        blackboard["refId::"+str(self.refId)]["utility"] = utility
        return utility

    #initial length processing
    def lenPre(self):
        length = 1
        blackboard["refId::"+str(self.refId)]["lenPre"] = length
        # print("LenPre: " + str(self.refId) + ", " + str(length))
        return length

    #final length processing
    def lenPost(self, extra):
        length = blackboard["refId::"+str(self.refId)]["lenPre"] + extra
        blackboard["refId::"+str(self.refId)]["lenPost"] = length
        # print("LenPost: " + str(self.refId) + ", " + str(length))
        return length

    #getting pairs of base id/count for a subtree
    def getAtionCount(self):
        dict = {}
        dict[self.baseId] = 1
        return dict

    #set action counts for subtree
    def setActionCounts(self, counts):
        blackboard["refId::"+str(self.refId)]["actionCount"] = counts[self.baseId]


#typical leaves of the tree
class ActionNode(Node):
    def __init__(self, preconditions, effects, baseId = -1, refId = -1, time = 1, effectText = "", involvedChars = "none", consentingChars = "none"):
        Node.__init__(self, baseId, refId) #constructor for nodes in general
        #set other properties
        self.effects = effects
        self.preconditions = preconditions
        self.time = time
        self.involvedChars = []
        self.effectText = effectText
        if involvedChars == "none":
            temp = []
            precond = getsource(preconditions)
            eff = getsource(effects)
            for a in agents:
                if "\""+a+"\"" in precond or "\""+a+"\"" in eff:
                    temp.append(a)
            self.involvedChars = temp
        else:
            self.involvedChars = involvedChars
        self.consentingChars = []
        if consentingChars == "none":
            self.consentingChars = ["$executingAgent$"]
        else:
            self.consentingChars = consentingChars

    def referrence(self):
        refIdNew = blackboard["refIdCount"]

        #creae entry for refid in blackboard
        if not "refId::"+str(refIdNew) in blackboard:
            blackboard["refId::"+str(refIdNew)] = {}

        blackboard["refIdCount"] += 1
        ref = ActionNode(self.preconditions, self.effects, baseId = self.baseId, refId = refIdNew, time = self.time, effectText = self.effectText, involvedChars = self.involvedChars, consentingChars = self.consentingChars)
        return ref

    def execute(self):
        #creae entry for refid in blackboard
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}

        #increment attempts on node (used for utility)
        blackboard["baseId::"+str(self.baseId)]["attempts"] += 1

        print("Exectuting: " + str(self.refId))

        #execute successfully if preconditions are met, fail if not
        if self.preconditions():
            print("SUCCESS")
            self.effects()
            blackboard["displayText"] += self.effectText
            return "SUCCESS"
        else:
            print("Failure")
            blackboard["baseId::"+str(self.baseId)]["failures"] += 1
            return "FAILURE"

    #utility calc, based on formula
    def utility(self):
        utility = 0
        #openness
        
        blackboard["refId::"+str(self.refId)]["utility"] = utility
        return utility

#parent of sequences and selectors
class CompositeNode(Node):
    def __init__(self, children, baseId = -1, refId = -1):
        Node.__init__(self, baseId, refId)
        self.children = children #list of child nodes

    #deepcopy, referrence of self with referrences of children
    def referrence(self):
        refIdNew = blackboard["refIdCount"]
        blackboard["refIdCount"] += 1
        childRefs = []
        for c in self.children:
            childRef = c.referrence()
            childRefs.append(childRef);
        ref = CompositeNode(childRefs, baseId = self.baseId, refId = refIdNew)
        return ref

    #parent node type, should never execute
    def execute(self):
        print("bad")
        for c in self.children:
            c.execute()
        return "SUCCESS"

    #print info
    def spec(self):
        print("Base ID: " + str(self.baseId) + "\n")
        print("Ref ID: " + str(self.refId) + "\n")
        print("Children: [")
        for c in self.children:
            c.spec()
        print("]\n")

    #utility calc, base, never called
    def utility(self):
        utility = 0
        blackboard["refId::"+str(self.refId)]["utility"] = utility
        return utility

    #initial length processing
    def lenPre(self):
        length = 0
        for c in self.children:
            length += c.lenPre()
        blackboard["refId::"+str(self.refId)]["lenPre"] = length
        # print("LenPre: " + str(self.refId) + ", " + str(length))
        return length

    #final length processing
    def lenPost(self, extra):
        length = blackboard["refId::"+str(self.refId)]["lenPre"]
        for c in self.children:
            childLen = length - blackboard["refId::"+str(c.refId)]["lenPre"]
            c.lenPost(extra + length - childLen)
        blackboard["refId::"+str(self.refId)]["lenPost"] = length + extra
        # print("LenPost: " + str(self.refId) + ", " + str(length+extra))
        return length + extra

    #getting pairs of base id/count for a subtree
    def getAtionCount(self):
        dict = {}
        for c in self.children:
            chDict = c.getAtionCount()
            for k in chDisct.keys():
                dict[k] = dict.get(k, 0) + chDisct[k]
        return dict

    #set action counts for subtree
    def setActionCounts(self, counts):
        for c in self.children:
            c.setActionCounts(counts)

#sequence, inherits everything but execute and referrence
class SequenceNode(CompositeNode):
    def execute(self):
        #make entry for refid
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}
            blackboard["refId::"+str(self.refId)]["currentIndex"] = 0;

        #execute next child
        status = self.children[blackboard["refId::"+str(self.refId)]["currentIndex"]].execute()

        if status == "SUCCESS":
            #keep going on success, save next index for next turn
            blackboard["refId::"+str(self.refId)]["currentIndex"] += 1
            if blackboard["refId::"+str(self.refId)]["currentIndex"] < len(self.children):
                return "RUNNING"
            else:
                #finish if no more children
                blackboard["refId::"+str(self.refId)]["currentIndex"] += 0
                return "SUCCESS"
        elif status == "RUNNING":
            return "RUNNING"
        else:
            return "FAILURE"

    #deepcopy, referrence of self with referrences of children
    def referrence(self):
        refIdNew = blackboard["refIdCount"]

        #creae entry for refid in blackboard
        if not "refId::"+str(refIdNew) in blackboard:
            blackboard["refId::"+str(refIdNew)] = {}

        blackboard["refIdCount"] += 1
        childRefs = []
        for c in self.children:
            childRef = c.referrence()
            childRefs.append(childRef);
        ref = SequenceNode(childRefs, baseId = self.baseId, refId = refIdNew)
        return ref

    #utility calc, average of children
    def utility(self):
        utilities = []
        for c in self.children:
            utilities.append(c.utility())
        utility = 0
        for u in utilities:
            utility += u
        utility = utility/len(utilities)
        blackboard["refId::"+str(self.refId)]["utility"] = utility
        return utility


#selector, inherits everything but execute and referrence
class SelectorNode(CompositeNode):
    def execute(self):
        #make entry for refid
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}
            blackboard["refId::"+str(self.refId)]["currentIndex"] = 0;

        #execute next child
        status = self.children[blackboard["refId::"+str(self.refId)]["currentIndex"]].execute()

        if status == "SUCCESS":
            return "SUCCESS"
        elif status == "RUNNING":
            return "RUNNING"
        else:
            #keep going on failure, save next index for next turn
            blackboard["refId::"+str(self.refId)]["currentIndex"] += 1
            if blackboard["refId::"+str(self.refId)]["currentIndex"] < len(self.children):
                return "RUNNING"
            else:
                #finish if no more children
                blackboard["refId::"+str(self.refId)]["currentIndex"] += 0
                return "FAILURE"

    #deepcopy, referrence of self with referrences of children
    def referrence(self):
        refIdNew = blackboard["refIdCount"]

        #creae entry for refid in blackboard
        if not "refId::"+str(refIdNew) in blackboard:
            blackboard["refId::"+str(refIdNew)] = {}

        blackboard["refIdCount"] += 1
        childRefs = []
        for c in self.children:
            childRef = c.referrence()
            childRefs.append(childRef);
        ref = SelectorNode(childRefs, baseId = self.baseId, refId = refIdNew)
        return ref

    #utility calc, max of children
    def utility(self):
        utilities = []
        for c in self.children:
            utilities.append(c.utility())
        utility = -2
        for u in utilities:
            if u > utility:
                utility = u
        blackboard["refId::"+str(self.refId)]["utility"] = utility
        return utility

    #initial length processing
    def lenPre(self):
        length = 0
        for c in self.children:
            length += c.lenPre()
        length /= len(self.children)
        blackboard["refId::"+str(self.refId)]["lenPre"] = length
        print("LenPre: " + str(self.refId) + ", " + str(length))
        return length

    #final length processing
    def lenPost(self, extra):
        length = blackboard["refId::"+str(self.refId)]["lenPre"]
        for c in self.children:
            c.lenPost(extra)
        blackboard["refId::"+str(self.refId)]["lenPost"] = length + extra
        print("LenPost: " + str(self.refId) + ", " + str(length+extra))
        return length + extra

#utility processing for sequences or selectors
def utilityProcess(tree):
    utilities = []
    for c in tree.children:
        c.lenPre()
        c.lenPost(0)
        c.setActionCounts(c.getAtionCount())
        utilities.append(c.utility())
    return utilities


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

#add an agent
def addAgent(agent):
    agents.append(agent)

#agent with associated personality
def addPersonalityAgent(agent, o, c, e, a, n):
    agents.append(agent)
    personality[agent] = {}
    personality[agent]["o"] = o
    personality[agent]["c"] = c
    personality[agent]["e"] = e
    personality[agent]["a"] = a
    personality[agent]["n"] = n

#every tree and agent pair
agentTrees = []

#make a tree/agent pair
def attachTreeToAgent(agent, tree):
    treeRef = tree.referrence()
    agentTrees.append((agent, treeRef))
    return treeRef

#variables
def setAgentVariable(agent, var, val):
    blackboard["variable::"+agent+"::"+var] = val

def getAgentVariable(agent, var):
    if not "variable::"+ agent +"::"+var in blackboard:
        print("Variable " + var + " not set!")
        return
    return blackboard["variable::"+ agent +"::"+var]

#execution
def turn():
    for t in agentTrees: #execute all trees
        setVariable("executingAgent", t[0])
        blackboard["displayText"] = ""
        t[1].execute()
        print("Effect Text: " + blackboard["displayText"])


#for later
#https://stackoverflow.com/questions/44206813/how-to-convert-function-to-str
