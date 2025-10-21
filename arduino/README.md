# Arduino Sketches for Solaris Conexus

This directory contains the Arduino code for the IoT devices in the Solaris Conexus project.

## Overview

The system consists of two types of houses:

- **Producer (`house_a`):** A house that generates solar energy and can sell the surplus.
- **Consumer (`house_b`):** A house that consumes energy from the grid and can buy energy from producers.

## Schematics

The Fritzing schematics for each house are located in their respective directories.

### House A (Producer)

![House A Schematic](house_a/House%20A.png)

_Fritzing file: `house_a/House A.fzz`_

### House B (Consumer)

![House B Schematic](house_b/House%20B.png)

_Fritzing file: `house_b/House B.fzz`_

## Code

- **`house_a/house_a.ino`:** The Arduino sketch for the producer house.
- **`house_b/house_b.ino`:** The Arduino sketch for the consumer house.
