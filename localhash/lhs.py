class LocalHash:

    @staticmethod
    def makeShingles(document, k=9):
        """
        :param document: an already processed string
        :param k: length of a kmer or shingle
        :return: set of k-length shingles
        """
        shingleSet = set(document[i:i+k] for i in range(len(document)-k+1))
        # TODO: hash the shingle
        # you could hash, so that you reduce from k bytes to length of hash bytes ...
        # why not use shorther k? shorter k reduces the uniqueness. Hash is more uniform than shorter ks..
        return shingleSet

    @staticmethod
    def shingle2hash(shingleset):
        """
        :param shingleset:
        :return: hashed shingleset
        """

    @staticmethod
    def jaccardDist(set1, set2):
        """
        :param set1:
        :param set2:
        :return:
        """
        sizeIntersect = 0
        for element in set1:
            if element in set2: sizeIntersect+=1
        sizeUnion = len(set1) + len(set2) - sizeIntersect
        return sizeIntersect/sizeUnion

    @staticmethod
    def sim2Doc(document1, document2):
        """
        :param document1: string of doc1
        :param document2: string of doc2
        :return: similarity
        """
        pass

    @staticmethod
    def sameDoc(document1, document2, threshold):
        """
        :param document1: string of doc1
        :param document2: string of doc1
        :param threshold: floatt that decides if two docs are the same
        :return: boolean
        """
        pass

if __name__ == "__main__":
    print(LocalHash.makeShingles("jon je avion", 9))
    print(LocalHash.jaccardDist({1, 2, 3, 4, 5, 6}, {1, 2, 3, 9, 10, 12}))