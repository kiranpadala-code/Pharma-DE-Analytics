{#
    Purpose:
    Override dbt's default schema naming convention to use
    custom schema names directly.

    Default behaviour:
    target_schema + '_' + custom_schema_name

    Custom behaviour:
    - Use the custom schema when specified.
    - Otherwise, use the default target schema.

    Schema mapping:
    staging      -> PHARMA_DB.STAGING
    intermediate -> PHARMA_DB.INT
    marts        -> PHARMA_DB.MARTS

    Note:
    This override removes default developer-level schema
    isolation and is intended for a single-developer project.
#}

{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}

{%- endmacro %}