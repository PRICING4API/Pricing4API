from loads import*


def imprime_lista(lista):
    for i in lista:
        print(i)


def test_load_pricings():
    print(imprime_lista(load_pricings("Pricing4API/data/Pricings.csv")))
    print("\n")

def test_filtra():
    print(imprime_lista(filtra(valores, "SendGrid")))
    print("\n")




    
    
    


if __name__ == "__main__":
    valores=load_pricings("Pricing4API/data/Pricings.csv")
    test_load_pricings()
    test_filtra()