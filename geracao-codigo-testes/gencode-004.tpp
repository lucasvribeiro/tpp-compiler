inteiro: n
inteiro: soma

inteiro principal()
	n := 3
	soma := 0
	repita
		soma := soma + n
		n := n - 1
	até n = 0
	
	n := 5
	retorna(soma)
fim
