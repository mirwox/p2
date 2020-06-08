
### Gazebo Turtlebot

Certifique-se de que seu `.bashrc` têm as variáveis `ROS_IP` e `ROS_MASTER_URI` desabilitadas antes e rodar o Gazebo.

Essas variáveis estarão desabilitadas se tiverem um `#` precedendo a linha. 

## Versão do Python

Os códigos ROS são compatíveis somente com Python 2.

Preficar executar as questões usando o comando `rosrun`. 

## Teleop

Sempre que usar o  `teleop` encerre o programa logo em seguida.  Enquanto estiver aberto o `teleop` ficará enviando comandos de velocidade para o robô, conflitando com seus programas que controlawm o robô. 



## catkin_make

Executar `catkin_make` após fazer o download do projeto: 

    cd ~/catkin_ws/
    catkin_make

## Onde baixar os arquivos

O código deve sempre ser baixado na pasta `cd ~/catkin_make/src` :

    cd ~/catkin_ws/src
    git clone <nome do repo>

## Arquivos executáveis

Certifique-se de que seus scripts Python são executáveis

    roscd p1_20
    cd scripts
    chmod a+x *py

## Executar prova

Para executar, faça:

    rosrun p1_20 arquivo.py 

Onde `arquivo.py` é algum script Python executável que você deve ter na pasta `p1_20/scripts`.


Certifique-se de que seus scripts ROS rodam com Python 2 e têm sempre no começo:

    #! /usr/bin/env python
    # -*- coding:utf-8 -*-
    
    from __future__ import division, print_function


## Commit no Github

    Lembre-se, de regularmente fazer
        cd ~/catkin_ws/src/PROVA
        git add --all
        git commit -m "Mensagem aqui"
        git push

