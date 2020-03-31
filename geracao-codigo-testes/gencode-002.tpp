{Condicional}
inteiro: a

inteiro principal()
	inteiro: ret
	
	a := 10    
	se a > 5 então
        ret := 100
    senão
        ret := 0
    fim

    a := 15
    retorna(ret)
fim
