# Checkout

## Purpose

Let a signed-in user pay for the cart.

## Users

Signed-in shoppers on web.

## Non-goals

No guest checkout. No saved cards.

## Constraints

PCI scope stays SAQ-A; payment fields live in the provider iframe.

## Success criteria

Checkout conversion is measurable per release.

## Requirements

### R-02 — Pay by card

- Statement: A signed-in user pays the cart total by card.
- Acceptance:
  - A successful charge creates an order with status paid.
  - A declined card shows the provider decline reason and keeps the cart.

### R-01 — Cancel order

- Statement: A signed-in user cancels a pending order.
- Acceptance:
  - A cancelled order changes status to cancelled.
