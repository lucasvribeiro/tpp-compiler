
inteiro soma(inteiro: a, inteiro:b)
	inteiro: c
	c := a + b
	retorna(c)
fim

inteiro principal()
	inteiro: a
	inteiro: b
	inteiro: c

	leia(a)
	leia(b)

	c := soma(a, b)

	escreva(c)

  retorna(0)
fim
