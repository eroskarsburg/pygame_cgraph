# Bomberman Game

Um jogo multiplayer local inspirado no clássico **Bomberman**, feito com **Python** e **Pygame**.

## 🎮 Como Jogar

Dois jogadores competem colocando bombas e evitando explosões. Cada jogador começa com 3 vidas. O último sobrevivente vence a partida!

### Controles

#### Jogador 1
- **Mover**: `W`, `A`, `S`, `D`
- **Colocar bomba**: `E`

#### Jogador 2
- **Mover**: Setas (`← ↑ ↓ →`)
- **Colocar bomba**: `ESPAÇO`

### Regras
- Máximo de 5 bombas simultâneas por partida.
- Bombas explodem após 5 segundos, criando uma cruz de fogo.
- Explosões causam **1 dano** ao jogador atingido.
- Quando um jogador perde todas as vidas, o outro vence.
- Tela de **Game Over** permite reiniciar ou sair.

## 🧱 Mapa

O mapa é construído com uma matriz de texto onde:
- `"W"` representa uma parede.
- Espaços `" "` são caminhos livres.

## ❤️ Vidas

As vidas de cada jogador são representadas na HUD superior com corações.

## 🛠 Requisitos

- Python 3.7+
- Pygame (`pip install pygame`)
- Conexão com a internet para carregar imagens de personagens, bombas e corações.

## ▶️ Como executar

1. Clone ou baixe este repositório.
2. Instale o pygame: 
    ```bash 
    pip install pygame