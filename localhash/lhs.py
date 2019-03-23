import binascii
import random

class LocalHash:

    def __init__(self, numHash=10):
        self.numHash = numHash
        self.maxPossible = 2 ** 32 - 1
        # src http://compoasso.free.fr/primelistweb/page/prime/liste_online_en.php
        self.prime = 4294967311
        self.alist, self.blist = self.getRandomCoeff(self.numHash)


    def makeShingles(self, document):
        """
        :param document: an already processed string
        :param k: length of a kmer or shingle
        :return: set of k-length shingles
        """
        doc = [word for word in document.split(" ") if word]
        shingleSet = set()
        for ind in range(0, len(doc)-2):
            kmer = doc[ind].strip()+" "+doc[ind+1].strip()+" "+doc[ind+2].strip()
            shingleSet.add(self.hashShingle(kmer.encode()))
        # you could hash, so that you reduce from k bytes to length of hash bytes ...
        # why not use shorther k? shorter k reduces the uniqueness. Hash is more uniform than shorter ks..
        return shingleSet


    def hashShingle(self, shingle):
        # hash shingle to 32bit integer
        crc = binascii.crc32(shingle) & 0xffffffff
        return crc


    def getRandomCoeff(self, k):

        # random hash function
        # h(x) = (a * x + b) % c

        # a, b random
        # c = prime

        # pick k random a,b
        alist = []
        blist = []
        while k > 0:
            randA = random.randint(0, self.maxPossible)
            randB = random.randint(0, self.maxPossible)
            # ensure unique rands
            while randA in alist:
                randA = random.randint(0, self.maxPossible)
            while randB in blist:
                randB = random.randint(0, self.maxPossible)
            alist.append(randA)
            blist.append(randB)
            k -= 1
        return alist, blist


    def makeMHsignature(self, document):
        signature = []
        for i in range(0, self.numHash):
            # track min hash val
            minHashVal = self.prime + 1 # max possible
            for hashedShingle in document:
                hashF = (self.alist[i]*hashedShingle + self.blist[i]) % self.prime

                if hashF < minHashVal:
                    minHashVal = hashF
            signature.append(minHashVal)
        return signature

    def doMost(self, document):
        return self.makeMHsignature(self.makeShingles(document))

    def compareSignatures(self, sig1, sig2):
        count = 0
        for k in range(len(sig1)):
            count += sig1[k] == sig2[k]
        return count/len(sig1)

    def equal(self, sig1, sig2, threshold=0.9):
        return True if self.compareSignatures(sig1, sig2) >= threshold else False





if __name__ == "__main__":
    document1 = "Tukaj ne bo nihce vec govoril Slovensko, ce se ne bomo borili proti okupatorju!"
    document2 = """
    Tukaj ne bo nihce vec govoril Slovensko, ce se ne bomo borili proti okupatorju!
    Tukaj ne bo nihce vec govoril Slovensko, ce se ne bomo borili proti okupatorju!
    Tukaj ne bo nihce vec govoril Slovensko, ce se ne bomo borili proti okupatorju!
    Tukaj ne bo nihce vec govoril Slovensko, ce se ne bomo borili proti okupatorju!
    """
    document3 = "Tukaj ne    bo nihce vec govorilSlovensko, cese ne bomo borili proti     okupatorju!"
    doc3 = """Tukaj ne bo nihce vec govoril Slovensko, ce se ne bomo borili proti okupatorju!
    Tukaj ne bo nihce vec govoril Slovensko, ce se ne bomo borili proti okupatorju!
    Tukaj ne bo nihce vec govoril Slovensko, ce se ne bomo borili proti okupatorju!
    Tukaj ne bo nihce vec govoril Slovensko, ce se ne bomo borili proti okupatorju!
    ALO"""
    document4 = "Tukaj ne bo nihce vec ce se ne bomo borili proti okupatorju!"
    document5 = """Kako smesno
    je bilo ko je cofko
    sel plavat.
    """
    sez = [document1, document2, document3, doc3, document4, document5]
    lhs = LocalHash()
    a = lhs.makeShingles(document1)
    b = lhs.makeShingles(document2)
    c = lhs.makeShingles(document3)
    lhs.makeShingles(document5)
    print(a)
    print(b)
    print(c)
    a, b, c = lhs.doMost(document1), lhs.doMost(document2), lhs.doMost(document3)
    print(lhs.equal(a, b))
    print(lhs.equal(a, c))
    print(lhs.equal(a, b))
    for doc in sez:
        for doc2 in sez:
            if doc != doc2:
                print(doc)
                print(doc2)
                print(lhs.equal(lhs.doMost(doc), lhs.doMost((doc2))))