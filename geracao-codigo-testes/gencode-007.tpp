
inteiro soma(inteiro: x, inteiro: y)
    inteiro: z
    z := x + y
    retorna(z)
fim

inteiro sub(inteiro: z, inteiro: t)
    inteiro: k
    k := z + t
    retorna(k)
fim

inteiro principal()
    inteiro: a
    inteiro: b
    inteiro: c
    inteiro: i
    inteiro: j
    inteiro: k

    i := 0

    repita
        leia(a)
        leia(b)
        j := soma(a,b)
        k := sub(a,b)
        c := soma(j, k)
        escreva(c)
        i := i + 1
    até i = 5

    retorna(0)
fim
