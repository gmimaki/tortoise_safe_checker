resource "aws_glue_catalog_database" "iotcore" {
  name = "iotcore"
}

resource "aws_glue_catalog_table" "temperature" {
  name = "temperature"
  database_name = aws_glue_catalog_database.iotcore.name

  table_type = "EXTERNAL_TABLE"

  parameters = {
    "EXTERNAL" = "TRUE"
  }

  partition_keys {
    name = "year"
    type = "int"
  }

  partition_keys {
    name = "month"
    type = "int"
  }

  partition_keys {
    name = "day"
    type = "int"
  }

  storage_descriptor {
    location = "s3://iotcore-gmimaki/"
    input_format = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      name = "temperature"
      serialization_library = "org.openx.data.jsonserde.JsonSerDe"

      parameters = {
        "paths" = "humidity,temperature,time"
      }
    }

    columns {
      name = "humidity"
      type = "double"
    }

    columns {
      name = "temperature"
      type = "double"
    }

    columns {
      name = "time"
      type = "double"
    }
  }
}