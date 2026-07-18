# Resource Queue Scheduling

Queue scheduling:

1. Kiem tra dependency.
2. Kiem tra resource.
3. Neu ready thi cap lease va chay.
4. Neu thieu resource thi `waiting_resource`.
5. Neu unsupported thi `blocked`.

Job dang `waiting_resource` khong duoc coi la failed va khong duoc chan cac job khac neu job khac du tai nguyen.
