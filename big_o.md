# Analise de Complexidade

## Variaveis usadas

- `k`: numero de iteracoes executadas pelo loop de monitoramento.
- `n`: numero de nos relevantes do DOM examinados para localizar o elemento.
- `d`: profundidade do elemento encontrado na arvore DOM. Vale `d <= n`.
- `a`: numero de alteracoes registradas no historico.

## Hipotese da analise

A analise abaixo considera o custo do algoritmo Python e da busca no DOM.
Latencia de rede, tempo de renderizacao do navegador e o atraso introduzido por
`time.sleep()` afetam o tempo real de execucao, mas nao mudam a classe de
complexidade assintotica do codigo.

## Custo das operacoes principais

- `carregar_pagina(url)`: `O(1)` do ponto de vista do algoritmo local.
  O metodo faz uma chamada ao driver e nao percorre estruturas proporcionais ao
  tamanho da entrada dentro do codigo Python.
- `localizar_elemento(seletor)`: `O(n)`.
  O Selenium precisa localizar o elemento no DOM com XPath ou CSS Selector.
- `_obter_xpath(elemento)`: `O(d)`.
  O script JavaScript sobe pela arvore ate a raiz para montar o XPath absoluto.
- Comparacao `valor_atual != valor_anterior`: `O(1)` para os valores tratados
  pelo projeto.
- Insercao em `historico.append(alteracao)`: `O(1)` amortizado.

## Complexidade do loop `monitorar`

### Carga inicial

Antes do loop, o metodo faz:

1. `carregar_pagina(url)` -> `O(1)`
2. `localizar_elemento(seletor)` -> `O(n)`

Portanto, a inicializacao custa `O(n)`.

### Uma iteracao do loop

Cada repeticao executa, no pior caso:

1. `time.sleep(intervalo)` -> `O(1)`
2. `carregar_pagina(url)` -> `O(1)`
3. `localizar_elemento(seletor)` -> `O(n)`
4. Comparacao do valor e possivel registro da alteracao -> `O(1)`

Como `O(1) + O(1) + O(n) + O(1) = O(n)`, cada iteracao custa `O(n)`.

### Total do monitoramento

Se o loop roda `k` vezes e cada iteracao custa `O(n)`, entao o custo total e:

`O(n) + k * O(n) = O(k * n)`

O termo inicial `O(n)` da carga inicial fica dominado por `k * O(n)` quando o
numero de iteracoes cresce.

## Complexidade espacial

- Estruturas temporarias por iteracao: `O(1)`
- Historico de alteracoes: `O(a)`

No pior caso, toda iteracao detecta uma mudanca. Como `a <= k`, o uso de memoria
fica em `O(k)` por causa da lista `historico`.

## Conclusao

- Tempo por iteracao do monitoramento: `O(n)`
- Tempo total do monitoramento: `O(k * n)`
- Memoria adicional: `O(a)`, com pior caso `O(k)`
