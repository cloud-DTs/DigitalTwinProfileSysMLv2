package MicroGridExampleMeta{
    public import DigitalTwinLibrary::*;

    part def MicroGridTwin specializes TwinEntity{
        part MicroGrid subsets entities {
            part battery subsets subEntities{
                part P12Sensor subsets twinComponents{
                    out port consumption subsets measurementPorts{
                        attribute consumption subsets measurement{
                            attribute dataType redefines dataType = AttributeDataType::DOUBLE;
                        }
                    }
                }

            }

            part charger subsets subEntities{
                part P13Sensor subsets twinComponents{
                    out port consumption subsets measurementPorts{
                        attribute consumption subsets measurement{
                            attribute dataType redefines dataType = AttributeDataType::DOUBLE;
                        }
                    }
                }
            }

            attribute MaxConsumption subsets const_attributes{
                attribute dataType redefines dataType = AttributeDataType::DOUBLE;
            }
        }
    }
}