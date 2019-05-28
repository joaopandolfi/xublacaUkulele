# xublacaUkulele
Ukulele Tunning

## Requisitos
* **Python 2.7**
* numpy
* pyaudio

```
pip install numpy
pip install pyaudio
```

## Usar
* Para afinação padrão

```
    +---------------------------------+
    | Ukulele |    Número da nota     |
    |   Tom   |  4  |  3  |  2  |  1  |
    +---------------------------------+
    |Standard | 392 | 262 | 330 | 440 |
    |         |  G  |  C  |  E  |  A  |
    +---------------------------------+

$ python2 xublacaUkulele.py
```

* Afinação **Barítono**
```
    +---------------------------------+
    |Baritone | 147 | 196 | 247 | 330 |
    |         |  D  |  G  |  B  |  A  |
    +---------------------------------+
$ python2 xublacaUkulele.py b    
```

* Afinação **D**
```
    +---------------------------------+
    |D-Tuning | 440 | 294 | 370 | 494 |
    |         |  A  |  D  |  F# |  B  |
    +---------------------------------+
$ python2 xublacaUkulele.py d
```

* Afinação **A Baixo**
```
    +---------------------------------+
    |Low A    | 220 | 294 | 370 | 494 |
    |         |  A  |  D  |  F# |  B  |
    +---------------------------------+
$ python xublacaUkulele.py a
```

* Afinação **G Baixo**
```
    +---------------------------------+
    |Low G    | 196 | 262 | 330 | 440 |
    |         |  G  |  C  |  E  |  A  |
    +---------------------------------+
$ python xublacaUkulele.py g
```


# Maintener
* João Carlos Pandolfi Santana
