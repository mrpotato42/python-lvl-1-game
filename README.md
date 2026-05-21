# 🏰 Arrow Defense

Un juego de defensa de torres en 2D desarrollado en Python con Pygame. Controla a un arquero, defiende tu fortaleza y recluta tropas aliadas para resistir oleadas de enemigos cada vez más intensas.

---

## 📋 Requisitos

- **Python** 3.11+
- **pygame-ce** 2.5+

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

---

## 🚀 Cómo ejecutar

Desde la raíz del proyecto:

```bash
python run.py
```

---

## 🎮 Controles

| Acción | Tecla / Ratón |
|---|---|
| Moverse izquierda / derecha | `A` / `D` o flechas |
| Subir al balcón de la torre | `W` (cerca de la torre) |
| Bajar al suelo | `S` |
| Cargar y apuntar flecha | Mantener clic izquierdo + arrastrar ratón |
| Disparar flecha | Soltar clic izquierdo |
| Reclutar Guerrero (50g) | `1` |
| Reclutar Arquero (75g) | `2` |
| Reclutar Caballero (150g) | `3` |
| Reclutar Catapulta (250g) | `4` |
| Pausar / Reanudar | `ESC` |
| Alternar lado de la torre (menú) | `T` |

---

## ⚔️ Mecánicas de juego

### El jugador
El jugador es un arquero que puede moverse libremente por el campo de batalla. Al mantenerse cerca de la torre, puede subir al **balcón** pulsando `W`, lo que lo protege de los ataques cuerpo a cuerpo enemigos y le da una mejor perspectiva para disparar.

El arco se carga manteniendo presionado el clic izquierdo. Se muestra una **línea guía punteada** que anticipa la trayectoria parabólica de la flecha en función del ángulo y la potencia acumulada.

> ⚠️ **Fuego amigo activo:** Las flechas del jugador pueden dañar a sus propias tropas. ¡Apunta bien!

### La torre
La torre es la estructura principal que debes proteger. Tiene **1000 puntos de salud** y está posicionada en uno de los laterales del mapa (izquierdo por defecto, configurable antes de empezar). Si su salud llega a 0, la partida termina.

### Las oleadas
Los enemigos llegan en oleadas progresivas. Entre oleada y oleada hay un breve descanso. La composición escala con el número de oleada:

| Oleada | Composición |
|---|---|
| 1 | 3 Guerreros |
| 2 | Guerreros + Arqueros |
| 3 | Guerreros + Caballeros + Arqueros |
| 4 | Todo tipo de unidades + Catapulta |
| 5+ | Composición aleatoria escalada |

### Economía (oro)
Al eliminar unidades enemigas ganas oro para reclutar tropas aliadas:

| Unidad | Recompensa |
|---|---|
| Guerrero | 70g |
| Arquero | 15g |
| Caballero | 150g |
| Catapulta | 200g |

---

## 🪖 Tropas aliadas

| Tropa | Coste | Salud | Daño | Rango | Especial |
|---|---|---|---|---|---|
| **Guerrero** | 50g | 120 | 15 | Cuerpo a cuerpo | Equilibrado, rápido |
| **Arquero** | 75g | 70 | 10 | 350 px | Disparo parabólico |
| **Caballero** | 150g | 250 | 25 | Cuerpo a cuerpo | Armadura: -35% daño recibido |
| **Catapulta** | 250g | 100 | 60 | 500 px | Daño en área (AoE), provoca temblor de pantalla |

---

## 🗂️ Estructura del proyecto

```
run.py                  # Punto de entrada
requirements.txt        # Dependencias
src/
├── main.py             # Inicialización de Pygame y ventana
├── game.py             # Bucle principal, oleadas, economía, cámara
├── config.py           # Todas las constantes y estadísticas del juego
├── entities/
│   ├── base_unit.py    # Clase base para todas las tropas
│   ├── units.py        # Guerrero, Arquero, Caballero, Catapulta
│   ├── player.py       # Control del jugador y mecánica del arco
│   ├── projectile.py   # Física de proyectiles y daño en área
│   └── tower.py        # Torre defensiva
├── physics/
│   ├── trajectory.py   # Cálculo de trayectorias parabólicas
│   └── collision.py    # Detección de colisiones AABB y circular
├── ui/
│   ├── hud.py          # Barras de salud, oro, oleadas, panel de reclutas
│   └── menu.py         # Menú principal, pausa, victoria/derrota
└── utils/
    └── particles.py    # Sistema de partículas (sangre, chispas, humo)
```

---

## ⚙️ Configuración rápida

Todos los parámetros del juego están centralizados en [`src/config.py`](src/config.py):

- `TOWER_SIDE` — lado de la torre (`"left"` o `"right"`)
- `GRAVITY` — gravedad que afecta a los proyectiles
- `GOLD_PER_KILL` — recompensa de oro por tipo de unidad eliminada
- `INITIAL_WAVE_GOLD` — oro inicial al comenzar la partida
- `ARROW_SPEED_MULTIPLIER` — velocidad de las flechas del jugador
- `PLAYER_MAX_CHARGE` — potencia máxima de carga del arco
- `STATS_WARRIOR / ARCHER / KNIGHT / CATAPULT` — estadísticas completas de cada tropa

---

## 🛠️ Tecnologías

- **Python 3.11+** con tipado estático (`from __future__ import annotations`)
- **pygame-ce 2.5** — motor de renderizado 2D y gestión de eventos
- Gráficos vectoriales procedurales (sin sprites externos)
- Sistema de partículas propio
- Física parabólica implementada desde cero
