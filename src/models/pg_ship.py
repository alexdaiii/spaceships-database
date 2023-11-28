from sqlalchemy import text, Engine

from src.database.db import get_session
import colorful as cf

pg_check_component_slots_func = text(
    """
    CREATE OR REPLACE FUNCTION check_component_slots_fnc() 
        RETURNS TRIGGER AS 
    $$
    DECLARE
        module_column_names TEXT[];
        module_column_name TEXT;
        module_components_used INTEGER;
        total_components_size_used INTEGER;
        max_component_in_class INTEGER;
        ship_class_name TEXT;
    BEGIN
        
        -- array of column names
        SELECT INTO module_column_names
        ARRAY[
            'small_component_slots',
            'medium_component_slots',
            'large_component_slots',
            'xlarge_component_slots',
            'titan_component_slots',
            'juggernaut_component_slots',
            'colossus_component_slots',
            'star_eater_component_slots'
        ];
        
        -- dynamically build query to get the sum of component slots used
        FOR module_column_name IN SELECT UNNEST(module_column_names) LOOP
            EXECUTE format(
                'SELECT %I 
                FROM spaceship_module 
                WHERE spaceship_module_id = %L',
                module_column_name,
                NEW.ship_module_id
            ) INTO module_components_used;
            
            -- if module_components_used >= 1 -> then it is the size of the module
            IF module_components_used >= 1 THEN
                EXECUTE format(
                    'SELECT SUM(ship_module_count)
                    FROM ship_template_to_module
                    JOIN spaceship_module ON spaceship_module.spaceship_module_id = ship_template_to_module.ship_module_id
                    WHERE ship_template_id = %L
                    AND spaceship_module.%I != 0',
                    NEW.ship_template_id,
                    module_column_name
                ) INTO total_components_size_used;
                
                EXECUTE format(
                    'SELECT SUM(%I)
                    FROM ship_class
                    JOIN ship_template ON ship_template.ship_class_id = ship_class.ship_class_id
                    WHERE ship_template_id = %L
                    LIMIT 1',
                    module_column_name,
                    NEW.ship_template_id
                ) INTO max_component_in_class;
                
                EXECUTE format(
                    'SELECT ship_class_name
                    FROM ship_class
                    JOIN ship_template ON ship_template.ship_class_id = ship_class.ship_class_id
                    WHERE ship_template_id = %L
                    LIMIT 1',
                    NEW.ship_template_id
                ) INTO ship_class_name;
                
                IF total_components_size_used > max_component_in_class THEN
                    RAISE EXCEPTION 'Ship template [id:%] has too many [%] modules. 
                    Ship class [%] only allows [%] [%] modules. Total [%] modules used', 
                    NEW.ship_template_id, 
                    module_column_name, 
                    ship_class_name,
                    max_component_in_class, 
                    module_column_name, 
                    total_components_size_used;
                    
                END IF;

                
            END IF;
            
        END LOOP;
        
        
        RETURN NEW;
        
    END;
    $$
    LANGUAGE 'plpgsql';
    """
)
pg_trg_1 = text(
    """
    DROP TRIGGER IF EXISTS check_component_slots_trg ON ship_template_to_module;
    """
)
pg_trg_2 = text(
    """   
    CREATE TRIGGER check_component_slots_trg
    AFTER INSERT OR UPDATE ON ship_template_to_module
    FOR EACH ROW EXECUTE PROCEDURE check_component_slots_fnc();
    """
)


def add_trigger(engine: Engine):
    if engine.dialect.name != "postgresql":
        print(
            cf.orange(
                f"Database triggers for {engine.dialect.name} "
                f"database have not been implemented"
            )
        )
        return

    with get_session(engine) as session:
        session.execute(pg_check_component_slots_func)
        session.execute(pg_trg_1)
        session.execute(pg_trg_2)


__all__ = ["add_trigger"]
