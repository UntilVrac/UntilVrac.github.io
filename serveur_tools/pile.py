class Pile :
    def __init__(self) :
        self.__content = []
    
    def est_vide(self) -> bool :
        return self.__content == []
    
    def empiler(self, e:any) -> None :
        self.__content.append(e)
    
    def depiler(self) -> any :
        if not self.est_vide() :
            return self.__content.pop(-1)
        
    def __str__(self) -> str :
        return "Pile : " + str(self.__content)
    
    def __repr__(self) -> str:
        return self.__str__()
    

if __name__ == "__main__" :
    p1 = Pile()
    assert p1.est_vide()
    p1.empiler(0)
    assert not p1.est_vide()
    p1.empiler(1)
    p1.empiler(2)
    print(p1)
    a = p1.depiler()
    print(a)
    assert a == 2