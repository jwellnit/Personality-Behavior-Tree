from dill.source import getsource
import math
import random

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

        self.refId = refId

    #create a deep copy of the node
    def referrence(self):
        refIdNew = blackboard["refIdCount"] #new refID
        blackboard["refIdCount"] += 1
        ref = Node(baseId = self.baseId, refId = refIdNew)
        return ref

    #execute the node
    def execute(self):
        return "SUCCESS"

    #print out identifying informaation
    def spec(self):
        print("{")
        print("Base ID: " + str(self.baseId))
        print("Ref ID: " + str(self.refId))
        print("}\n")

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
        if getVariable("maxAttempts") < blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["attempts"]:
            setVariable("maxAttempts", blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["attempts"])

    def initialize(self):
        #creae entry for refid in blackboard
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}

        if not "agent::"+str(getVariable("executingAgent")) in blackboard:
            blackboard["agent::"+str(getVariable("executingAgent"))] = {}
            blackboard["agent::"+str(getVariable("executingAgent"))] = {}

        if not "baseId::"+str(self.baseId) in blackboard["agent::"+str(getVariable("executingAgent"))]:
            blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)] = {}


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
            temp.append("$executingAgent$")
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

        # #creae entry for refid in blackboard
        # if not "refId::"+str(refIdNew) in blackboard:
        #     blackboard["refId::"+str(refIdNew)] = {}

        blackboard["refIdCount"] += 1
        ref = ActionNode(self.preconditions, self.effects, baseId = self.baseId, refId = refIdNew, time = self.time, effectText = self.effectText, involvedChars = self.involvedChars, consentingChars = self.consentingChars)
        return ref

    def execute(self):
        # print(str(self.refId))

        #creae entry for refid in blackboard
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}
            blackboard["refId::"+str(self.refId)]["ticks"] = self.time

        if not "agent::"+str(getVariable("executingAgent")) in blackboard:
            blackboard["agent::"+str(getVariable("executingAgent"))] = {}
            blackboard["agent::"+str(getVariable("executingAgent"))] = {}

        if not "baseId::"+str(self.baseId) in blackboard["agent::"+str(getVariable("executingAgent"))]:
            blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)] = {}
            blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["failures"] = 0
            blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["attempts"] = 0

        #increment attempts on node (used for utility)
        blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["attempts"] += 1

        #print("Exectuting: " + str(self.refId))

        #execute successfully if preconditions are met, fail if not
        if self.preconditions():
            blackboard["refId::"+str(self.refId)]["ticks"] = blackboard["refId::"+str(self.refId)]["ticks"] - 1
            if blackboard["refId::"+str(self.refId)]["ticks"] > 0:
                return "RUNNING"
            # print("SUCCESS")
            self.effects()
            blackboard["displayText"] += self.effectText
            blackboard["refId::"+str(self.refId)]["ticks"] = self.time
            return "SUCCESS"
        else:
            # print("Failure")
            blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["failures"] += 1
            blackboard["refId::"+str(self.refId)]["ticks"] = self.time
            return "FAILURE"

    #utility calc, based on formula
    def utility(self):
        utility = 0

        #openness
        #attempts made of this action type
        o1 = 0
        if getVariable("maxAttempts") > 0:
            o1 = 1 - blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["attempts"]/getVariable("maxAttempts")
            o1 = o1*2 - 1

        #number of occurances/size of branch
        o2 = 1 - blackboard["refId::"+str(self.refId)]["actionCount"]/blackboard["refId::"+str(self.refId)]["lenPost"]
        o2 = o2*2 - 1
        #failures over attempts
        o3 = 0
        if blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["attempts"] > 0:
            o3 = 1 - blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["failures"]/blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["attempts"]
            o3 = o3*2 - 1
        #combine
        o = (o1+o2+o3)/3
        o *= personality[str(getVariable("executingAgent"))]["o"]
        o = (o+1)/2

        #conscientiousness
        #whether or not you are a consenting character
        c1 = int("$executingAgent$" in self.consentingChars or str(getVariable("executingAgent")) in self.consentingChars)
        c1 = c1*2 - 1
        #length of branch
        c2 = 1 - blackboard["refId::"+str(self.refId)]["lenPost"]/getVariable("maxLength")
        c2 = c2*2 - 1
        #combine
        c = (c1+c2)/2
        c *= personality[str(getVariable("executingAgent"))]["c"]
        c = (c+1)/2

        consentingChars = self.consentingChars.copy()
        if "$executingAgent$" in consentingChars:
            consentingChars.remove("$executingAgent$")
        if str(getVariable("executingAgent")) in consentingChars:
            consentingChars.remove(str(getVariable("executingAgent")))
        involvedChars = self.involvedChars.copy()
        if "$executingAgent$" in involvedChars:
            involvedChars.remove("$executingAgent$")
        if str(getVariable("executingAgent")) in involvedChars:
            involvedChars.remove(str(getVariable("executingAgent")))
        #extraversion
        #porportion of consenting characters
        e1 = len(consentingChars)/len(agents)
        e1 = e1*2 - 1
        #porportion of non consenting characters
        e2 = len(set(involvedChars) - set(consentingChars))/len(agentTrees)
        e2 = e2*2 - 1
        #combine
        e = (e1+e2)/2
        e *= personality[str(getVariable("executingAgent"))]["e"]
        e = (e+1)/2

        #Agreeableness
        #porportion of consenting characters
        a1 = len(consentingChars)/len(agents)
        a1 = a1*2 - 1
        #porportion of non consenting characters
        a2 = 1 - len(set(involvedChars) - set(consentingChars))/len(agentTrees)
        a2 = a2*2 - 1
        #combine
        a = (a1+a2)/2
        a *= personality[str(getVariable("executingAgent"))]["a"]
        a = (a+1)/2

        #neuroticism
        #failures over attempts
        n = 0
        if blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["attempts"] > 0:
            n = 1 - blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["failures"]/blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["attempts"]
            n = n*2 - 1
        n *= personality[str(getVariable("executingAgent"))]["n"]
        n = (n+1)/2

        #get final utility val
        utility = math.sqrt(o**2 + c**2 + e**2 + a**2 + n**2)

        blackboard["refId::"+str(self.refId)]["utility"] = utility
        return utility

    def initialize(self):
        #creae entry for refid in blackboard
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}
            blackboard["refId::"+str(self.refId)]["ticks"] = self.time

        if not "agent::"+str(getVariable("executingAgent")) in blackboard:
            blackboard["agent::"+str(getVariable("executingAgent"))] = {}
            blackboard["agent::"+str(getVariable("executingAgent"))] = {}

        if not "baseId::"+str(self.baseId) in blackboard["agent::"+str(getVariable("executingAgent"))]:
            blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)] = {}
            blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["failures"] = 0
            blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)]["attempts"] = 0

#parent of sequences and selectors
class CompositeNode(Node):
    def __init__(self, children, baseId = -1, refId = -1, printOut = ""):
        Node.__init__(self, baseId, refId)
        self.children = children #list of child nodes
        self.printOut = printOut

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
        print("{")
        print("Base ID: " + str(self.baseId))
        print("Ref ID: " + str(self.refId))
        print("Children: [")
        for c in self.children:
            print(c.refId)
        print("]")
        print("}\n")
        for c in self.children:
            c.spec()

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
            for k in chDict.keys():
                dict[k] = dict.get(k, 0) + chDict[k]
        return dict

    #set action counts for subtree
    def setActionCounts(self, counts):
        for c in self.children:
            c.setActionCounts(counts)

    def initialize(self):
        #creae entry for refid in blackboard
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}
            blackboard["refId::"+str(self.refId)]["currentIndex"] = 0;

        if not "agent::"+str(getVariable("executingAgent")) in blackboard:
            blackboard["agent::"+str(getVariable("executingAgent"))] = {}
            blackboard["agent::"+str(getVariable("executingAgent"))] = {}

        if not "baseId::"+str(self.baseId) in blackboard["agent::"+str(getVariable("executingAgent"))]:
            blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)] = {}

        for c in self.children:
            c.initialize()

#sequence, inherits everything but execute and referrence
class SequenceNode(CompositeNode):
    def execute(self):
        # print(str(self.refId))
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
                blackboard["refId::"+str(self.refId)]["currentIndex"] = 0
                return "SUCCESS"
        elif status == "RUNNING":
            return "RUNNING"
        else:
            blackboard["refId::"+str(self.refId)]["currentIndex"] = 0
            return "FAILURE"

    #deepcopy, referrence of self with referrences of children
    def referrence(self):
        refIdNew = blackboard["refIdCount"]

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
        # print(str(self.refId))
        #make entry for refid
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}
            blackboard["refId::"+str(self.refId)]["currentIndex"] = 0;

        #execute next child


        while(True):
            status = self.children[blackboard["refId::"+str(self.refId)]["currentIndex"]].execute()
            if status == "SUCCESS":
                blackboard["refId::"+str(self.refId)]["currentIndex"] = 0
                return "SUCCESS"
            elif status == "RUNNING":
                return "RUNNING"
            else:
                #keep going on failure, save next index for next turn
                blackboard["refId::"+str(self.refId)]["currentIndex"] += 1
                if blackboard["refId::"+str(self.refId)]["currentIndex"] >= len(self.children):
                    #finish if no more children
                    blackboard["refId::"+str(self.refId)]["currentIndex"] = 0
                    return "FAILURE"

    #deepcopy, referrence of self with referrences of children
    def referrence(self):
        refIdNew = blackboard["refIdCount"]

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
        #print("LenPre: " + str(self.refId) + ", " + str(length))
        return length

    #final length processing
    def lenPost(self, extra):
        length = blackboard["refId::"+str(self.refId)]["lenPre"]
        for c in self.children:
            c.lenPost(extra)
        blackboard["refId::"+str(self.refId)]["lenPost"] = length + extra
        #print("LenPost: " + str(self.refId) + ", " + str(length+extra))
        return length + extra


def waitPrecond():
    return True

def waitEffects():
    return

wait = ActionNode(waitPrecond,
                    waitEffects,
                    effectText = "Wait. ",
                    involvedChars = ["$executingAgent$"],
                    consentingChars = [])




#orders branches at execute based on utility
class SelectorUtilityNode(SelectorNode):
    def execute(self):

        # print(str(self.refId))
        if getVariable("executingAgent") in personality:
            #get utilities
            utilities = utilityProcess(self)

            pairs = []
            for i in range(len(utilities)):
                pairs.append((utilities[i], self.children[i]))

            #sort pairs
            pairs.sort(key = lambda pair: pair[0])

            sorted = []
            for p in pairs:
                sorted.append(p[1])

            self.children = sorted

            #print(pairs)

        #make entry for refid
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}
            blackboard["refId::"+str(self.refId)]["currentIndex"] = 0;



        while(True):
            #execute next child
            status = self.children[blackboard["refId::"+str(self.refId)]["currentIndex"]].execute()
            if status == "SUCCESS":
                blackboard["refId::"+str(self.refId)]["currentIndex"] = 0
                return "SUCCESS"
            elif status == "RUNNING":
                return "RUNNING"
            else:
                #keep going on failure, save next index for next turn
                blackboard["refId::"+str(self.refId)]["currentIndex"] += 1
                if blackboard["refId::"+str(self.refId)]["currentIndex"] >= len(self.children):
                    #finish if no more children
                    blackboard["refId::"+str(self.refId)]["currentIndex"] = 0
                    return "FAILURE"

    #deepcopy, referrence of self with referrences of children
    def referrence(self):
        refIdNew = blackboard["refIdCount"]

        blackboard["refIdCount"] += 1
        childRefs = []
        for c in self.children:
            childRef = c.referrence()
            childRefs.append(childRef);
        ref = SelectorUtilityNode(childRefs, baseId = self.baseId, refId = refIdNew)
        return ref

#sequence, uses utility to automatically fail sometimes
class SequenceUtilityNode(SequenceNode):
    def execute(self):
        if self.printOut != "":
            print(self.printOut)
        # print(str(self.refId))
        #make entry for refid
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}
            blackboard["refId::"+str(self.refId)]["currentIndex"] = 0;


        if getVariable("executingAgent") in personality:
            #get utilities
            utilities = utilityProcess(self)

            #likelihood of failure of next child
            n = personality[str(getVariable("executingAgent"))]["n"]
            n = (n+1)/2
            u = utilities[blackboard["refId::"+str(self.refId)]["currentIndex"]]
            u = u/math.sqrt(5)
            p = (n*u)/10
            if random.random() <= p:
                blackboard["refId::"+str(self.refId)]["currentIndex"] = 0
                print("Change Mind")
                return "FAILURE"

            #execute next child
            status = self.children[blackboard["refId::"+str(self.refId)]["currentIndex"]].execute()

            if status == "SUCCESS":
                #keep going on success, save next index for next turn
                blackboard["refId::"+str(self.refId)]["currentIndex"] += 1
                if blackboard["refId::"+str(self.refId)]["currentIndex"] < len(self.children):
                    return "RUNNING"
                else:
                    #finish if no more children
                    blackboard["refId::"+str(self.refId)]["currentIndex"] = 0
                    return "SUCCESS"
            elif status == "RUNNING":
                return "RUNNING"
            else:
                #likelihood of retry
                n = personality[str(getVariable("executingAgent"))]["n"]
                n = (n+1)/2
                c = personality[str(getVariable("executingAgent"))]["c"]
                c = (c+1)/2
                u = utilities[blackboard["refId::"+str(self.refId)]["currentIndex"]]
                u = u/math.sqrt(5)
                p1 = n*u
                p2 = c*u
                p = math.sqrt((p1*p1) + (p2*p2))/math.sqrt(2)
                if random.random() <= p:
                    wait.execute()
                    return "RUNNING"
                else:
                    blackboard["refId::"+str(self.refId)]["currentIndex"] = 0
                    return "FAILURE"

        else:
            #execute next child
            status = self.children[blackboard["refId::"+str(self.refId)]["currentIndex"]].execute()

            if status == "SUCCESS":
                #keep going on success, save next index for next turn
                blackboard["refId::"+str(self.refId)]["currentIndex"] += 1
                if blackboard["refId::"+str(self.refId)]["currentIndex"] < len(self.children):
                    return "RUNNING"
                else:
                    #finish if no more children
                    blackboard["refId::"+str(self.refId)]["currentIndex"] = 0
                    return "SUCCESS"
            elif status == "RUNNING":
                return "RUNNING"
            else:
                blackboard["refId::"+str(self.refId)]["currentIndex"] = 0
                return "FAILURE"

    #deepcopy, referrence of self with referrences of children
    def referrence(self):
        refIdNew = blackboard["refIdCount"]

        blackboard["refIdCount"] += 1
        childRefs = []
        for c in self.children:
            childRef = c.referrence()
            childRefs.append(childRef);
        ref = SequenceUtilityNode(childRefs, baseId = self.baseId, refId = refIdNew, printOut = self.printOut)
        return ref

#guard
class GuardNode(CompositeNode):
    def __init__(self, preconditions, child, baseId = -1, refId = -1):
        Node.__init__(self, baseId, refId)
        self.child = child #child node
        self.preconditions = preconditions

    #deepcopy, referrence of self with referrences of children
    def referrence(self):
        refIdNew = blackboard["refIdCount"]
        blackboard["refIdCount"] += 1
        childRef = self.child.referrence()
        ref = GuardNode(self.preconditions, childRef, baseId = self.baseId, refId = refIdNew)
        return ref

    #parent node type, should never execute
    def execute(self):
        # print(str(self.refId))
        if self.preconditions():
            return self.child.execute()
        else:
            return "FAILURE"

    #print info
    def spec(self):
        print("Base ID: " + str(self.baseId))
        print("Ref ID: " + str(self.refId))
        print("Child: ")
        self.child.spec()
        print("\n")

    #utility calc, base, never called
    def utility(self):
        utility = 0
        if self.preconditions():
            utility = self.child.utility()
        blackboard["refId::"+str(self.refId)]["utility"] = utility
        return utility

    #initial length processing
    def lenPre(self):
        length = self.child.lenPre()
        blackboard["refId::"+str(self.refId)]["lenPre"] = length
        # print("LenPre: " + str(self.refId) + ", " + str(length))
        return length

    #final length processing
    def lenPost(self, extra):
        length = blackboard["refId::"+str(self.refId)]["lenPre"]
        childLen = length - blackboard["refId::"+str(self.child.refId)]["lenPre"]
        self.child.lenPost(extra + childLen)
        blackboard["refId::"+str(self.refId)]["lenPost"] = length + extra
        # print("LenPost: " + str(self.refId) + ", " + str(length+extra))
        return length + extra

    #getting pairs of base id/count for a subtree
    def getAtionCount(self):
        dict = self.child.getAtionCount()
        return dict

    #set action counts for subtree
    def setActionCounts(self, counts):
        self.child.setActionCounts(counts)

    def initialize(self):
        #creae entry for refid in blackboard
        if not "refId::"+str(self.refId) in blackboard:
            blackboard["refId::"+str(self.refId)] = {}
            blackboard["refId::"+str(self.refId)]["currentIndex"] = 0;

        if not "agent::"+str(getVariable("executingAgent")) in blackboard:
            blackboard["agent::"+str(getVariable("executingAgent"))] = {}
            blackboard["agent::"+str(getVariable("executingAgent"))] = {}

        if not "baseId::"+str(self.baseId) in blackboard["agent::"+str(getVariable("executingAgent"))]:
            blackboard["agent::"+str(getVariable("executingAgent"))]["baseId::"+str(self.baseId)] = {}

        self.child.initialize()

    #print info
    def spec(self):
        print("{")
        print("Base ID: " + str(self.baseId))
        print("Ref ID: " + str(self.refId))
        print("Child: " + str(self.child.refId))
        print("}\n")
        self.child.spec()



#utility processing for sequences or selectors
def utilityProcess(tree):
    utilities = []
    setVariable("maxLength", 0)
    setVariable("maxAttempts", 0)
    for c in tree.children:
        c.initialize()
        c.lenPre()
        leng = c.lenPost(0)
        if leng > getVariable("maxLength"):
            setVariable("maxLength", leng)
        c.setActionCounts(c.getAtionCount())
    for c in tree.children:
        utilities.append(c.utility())
    return utilities


#variables
def setVariable(var, val):
    if var[0] == '$' and var[-1] == '$':
        var = getVariable(var[1:-1])
    if type(val) == type("test") and val[0] == '$' and val[-1] == '$':
        val = getVariable(val[1:-1])
    blackboard["variable::"+var] = val

def getVariable(var):
    if var[0] == '$' and var[-1] == '$':
        var = getVariable(var[1:-1])
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
    if var[0] == '$' and var[-1] == '$':
        var = getVariable(var[1:-1])
    if type(val) == type("test") and val[0] == '$' and val[-1] == '$':
        val = getVariable(val[1:-1])
    if agent[0] == '$' and agent[-1] == '$':
        agent = getVariable(agent[1:-1])
    blackboard["variable::"+agent+"::"+var] = val

def getAgentVariable(agent, var):
    if var[0] == '$' and var[-1] == '$':
        var = getVariable(var[1:-1])
    if agent[0] == '$' and agent[-1] == '$':
        agent = getVariable(agent[1:-1])
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
        print(t[0]+ "::Effect Text: " + blackboard["displayText"])


#for later
#https://stackoverflow.com/questions/44206813/how-to-convert-function-to-str
