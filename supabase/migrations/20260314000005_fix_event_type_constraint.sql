-- Extend event_type check constraint to include Pokémon TCG event types.
-- The original constraint (migration 000001) only covered the initial 5 values.
-- pokemon_tcg and product_drop were added to models later but never landed in the DB.

alter table events
  drop constraint if exists events_event_type_check;

alter table events
  add constraint events_event_type_check
    check (event_type in (
      'event',
      'deal',
      'birthday_freebie',
      'amusement',
      'seasonal',
      'pokemon_tcg',
      'product_drop'
    ));
