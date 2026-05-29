# Entradas do Sistema

Os componentes utilizados no sistema são:

- Potenciômetro (A0)
- Sensor IR (D6)
- Botão (opcional, D2)
- LED RGB (D9,D10 e D11)
- Buzzer (D5)

---

# Variáveis do Sistema

O sistema trabalha com as seguintes variáveis:

- `potenciometro` → valores de 0 a 1023
- `ir` → estado digital (0 ou 1)
- `estadoSistema` → NORMAL / ALERTA / CRÍTICO
- `buzzer` → ligado ou desligado
- `led` → cor ou status

---

# Regras do Sistema

## Regra 1 — Alerta de Potenciômetro
SE potenciômetro > 700
ENTÃO estado = ALERTA
E ligar buzzer
E acender LED vermelho

## REGRA 2 — NORMALIDADE
SE potenciômetro <= 700
ENTÃO estado = NORMAL
E buzzer desligado
E LED verde

## REGRA 3 — SENSOR IR
SE IR = 1
ENTÃO registrar evento "MOVIMENTO DETECTADO"
E enviar para API

## REGRA 4 — SEGURANÇA DO SISTEMA
SE múltiplos alertas consecutivos
ENTÃO estado = CRÍTICO

## FLUXO DE DECISÃO (O QUE VOCÊ VAI DESCREVER NO TRABALHO)
LER sensores
    ↓
VERIFICAR regras
    ↓
DECIDIR estado
    ↓
EXECUTAR ação (LED / buzzer)
    ↓
GERAR JSON
    ↓
ENVIAR via Wi-Fi (TCP/IP)


---

# Exemplo de Estado do Sistema (JSON)

```json
{
  "potenciometro": 750,
  "ir": 1,
  "estado": "ALERTA",
  "buzzer": 1,
  "led": "vermelho"
}
  "buzzer": 1,
  "led": "vermelho"
}
