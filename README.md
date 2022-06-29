# TP Bioinformatica

## Requisitos
La mayoria de los ejercicios estan resueltos usando Python y Biopython. Para poder ejecutarlos,
es necesario tener `python 3` (probado con `python 3.8.9`) y las dependencias instaladas:

```bash
pip install -r requirements.txt
```

Cada ejercicio hecho en python imprime su uso cuando se lo llama sin argumentos 
(o con argumentos invalidos).


## Ejercicio 1
Para obtener informacion sobre su uso:
```bash
python3 Ej1.py
```

Ejemplo:

```bash
python3 Ej1.py sequence.gb -o 'out1/out' -l 300
```

## Ejercicio 2
```bash
python3 Ej2.py
```

Ejemplo:

```bash
python3 Ej2.py -f out1/out.fasta -r in2/blast.xml
```

## Ejercicio 3
Para hacer un MSA local, es posible usar [MUSCLE](http://www.drive5.com/muscle/).
Si el mismo no es especificado, se realiza utilizando Biopython directamente.

```bash
python3 Ej3.py
```

Ejemplo:

```bash
python3 Ej3.py in3/sequence.fasta
```
