import inspect

from fastapi_llm_test_generator.schemas import Walker


def use_db_plugin(plugin_instance, route: Walker) -> Walker:
    tables = []
    table = plugin_instance.extract_table_names(route.source_code)
    if table:
        tables.extend(table)

    if route.function_calls:
        for name, func in route.function_calls.items():
            print("=>", func)
            try:
                func_source_code = inspect.getsource(func)
            except Exception as e:
                continue
            table = plugin_instance.extract_table_names(func_source_code)
            if table:
                tables.extend(table)

    for table in tables:
        try:
            table_def = plugin_instance.get_table_definitions(table_name=table)
        except Exception as e:  # TODO catch DB Errors
            continue
        markdown = plugin_instance.generate_markdown(table, *table_def)

        route.table_markdowns.append(markdown)
        route.table_defs[table] = table_def
    return route


async def async_use_db_plugin(plugin_instance, route: Walker) -> Walker:
    tables = []
    table = plugin_instance.extract_table_names(route.source_code)
    if table:
        tables.extend(table)

    if route.function_calls:
        for name, func in route.function_calls.items():
            func_source_code = inspect.getsource(func)
            table = plugin_instance.extract_table_names(func_source_code)
            if table:
                tables.extend(table)

    for table in tables:
        table_def = await plugin_instance.get_table_definitions(table_name=table)
        markdown = plugin_instance.generate_markdown(table, *table_def)

        route.table_markdowns.append(markdown)
        route.table_defs[table] = table_def

    return route
