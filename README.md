# DigitalTwinSysmlv2CM
## Prerequisites
- docker
- python
- a .sysml input file with model which uses the Digital
## Setup
```bash
python -m venv venv
```
```bash
#Ubuntu
source venv/bin/activate
```
Start docker
```bash
cd apiserver
sh build.sh
cd ..
```
### Execution
place your sysml files in the src/sysmlfiles directory
```bash
python -m src.main ./src/sysmlfiles/
```
The json for the deployer will be then in the ouptut folder.
## DigitalTwinLibrary – Definition & Usage Concept
### 1. Core Concept: The Casing Rule
All user-defined keywords follow a strict DEFINITION vs. USAGE pattern to separate abstract types from actual deployable instances.

- Capitalized Keyword (#Entity) → DEFINITION (Type-Level)
- Lowercase Keyword (#entity)   → USAGE (Instance-Level)

---


### 2. Definition Keywords (Type-Level)
Applied to `def` blocks to introduce reusable types into the model.

- #Twin: Defines the root container and global storage/retention policies.
- #Entity: Defines a logical or physical object template (e.g., a Battery or a Building).
- #Component: Defines a functional unit template that contains sensors/actuators.
- #Condition: Defines a rule template for monitoring and logic.
- #MeasureAttribute: Defines a telemetry data point template.
- #ConstAttribute: Defines a static configuration property template.

---

### 3. Usage Keywords (Instance-Level)
Applied to properties or blocks to instantiate a Definition. These represent concrete, deployable elements.

#### #entity
- Hierarchy: Must exist within a #Twin or another #entity.
- Purpose: Represents a physical/logical asset instance.
- Constraint: Missing a valid parent triggers an error.

#### #component
- Hierarchy: Must exist within a valid #entity.
- Purpose: Groups measurements and functional logic for a specific device.
- Constraint: If the parent #entity is missing, mapping fails.

#### #measureAttribute
- Hierarchy: Must be defined inside a #component.
- Purpose: Represents live telemetry data (e.g., temperature, consumption).
- Attributes: 
    - dataType: [INTEGER; DOUBLE; STRING]
- Example:
    ```sysml
    #measureAttribute consumption {
        :>> dataType default AttributeDataType::DOUBLE;
    }
    ```

#### #constAttribute
- Hierarchy: Must exist inside an #entity.
- Purpose: Represents static metadata (e.g., max capacity, serial number).
- Attributes:
    - value: The actual string representation of the constant.
    - dataType: [INTEGER; DOUBLE; STRING]

#### #condition
- Hierarchy: Must exist within a #Twin.
- Purpose: Defines the logic for an automated action (e.g., "If A > B").
- Elements: Requires leftOperand, operator, and rightOperand.

#### #strategyAction
- Hierarchy: Must exist inside a #condition.
- Purpose: The specific task to execute when a condition is met (e.g., Lambda function).
- Validation: `customPayload` must be a valid JSON string.

#### Feedback Scenarios:
1. **EXTERN:** When `external` is set to `true`, the deployer assumes the function is already hosted externally. It will not upload code but requires an `externalTopic`.
    ```sysml
    #strategyAction alertAction {
        :>> name = "Alert Action";
        :>> external = true;
        :>> feedbackTopicType = FeedbackTopicType::EXTERN;
        :>> externalTopic = "EXTERN_TPIC";
        :>> customPayload = "{\"message\":\"High Consumption Alert\"}";
    }
    ```
2. **INTERN:** Result is sent back to a system component. Use the key `componentTopic` to target a component.
    ```sysml
    #strategyAction alertAction2 {
        :>> feedbackTopicType = FeedbackTopicType::INTERN;
        :>> componentTopic = MicroGrid.battery.p12;
    }
    ```
3. **NOFEEDBACK (Default):** If the type is not set, it defaults to `NOFEEDBACK`. The system assumes the function returns nothing and performs no downstream messaging.

---

### 4. Inheritance, Redefinition & Keyword Elision

The DigitalTwinProfile supports SysML v2 inheritance patterns to keep models clean and readable.

#### 4.1 Keyword Elision (Semantic Inheritance)
If a usage redefines or subsets an element that was already marked with a user-defined keyword higher up in the hierarchy, the hashtag keyword can be omitted.
- The parser recognizes the semantic identity through the redefinition chain.
- For subsetting when y inherited and not subsetted the parser will use this. When you subsett it then it will use the subsetted feature.
- **Example:** If `maxConsumption` is defined as a `#constAttribute` in a parent `Entity`, the redefinition `mComp :>> maxConsumption` is automatically treated as a `#constAttribute` without needing the hashtag again.

#### 4.2 Renaming during Redefinition
When redefining, the attribute name can be changed to fit the local context.
- The Digital Twin mapping will use the **new name** (left of the colon).
- **Example:** `mComp :>> maxConsumption` results in a property named "mComp" in the twin.

#### 4.3 Attribute Value Mapping
Also the default value for example for a #constAttribute will be searched through the hierarchy. You see more in the example below.
Internal fields (like `value`) should be mapped using redefinition for initialization.
- **Example:** ` :>> value default "23.0"` maps a local attribute to the constant's data field.
also possible renaming(which will have no effect o the deplyoment)
- **Example:** `value2 :>> value default "23.0"`.


---

### 5. Formal Constraints & Multiplicities

1. **Parent-Child Integrity:** The strict hierarchy (#Twin -> #entity -> #component -> #measureAttribute) is mandatory.

2. **Multiplicities:** Multiplicities (e.g., [0..*]) on user-defined keywords are **NOT allowed**. Every usage must map 1:1 to a unique resource.

3. **Unique IDs:** Each usage receives a stable UUID generated from its hierarchical path string. This ensures idempotency and prevents duplicate resources on re-runs.

4. **Nonames** are not allowed
```sysml
#Component <here has to be a name> def {

}
```
---

### 6. Example Mapping

```sysml
package MG {

    private import MetaModelDigitalTwin::*;

    #Component def PAC_Sensor {
        #measureAttribute consumption {
            :>> dataType default AttributeDataType::DOUBLE;
        }
        attribute test;
    }

    abstract #Entity def AbstractEntity {
        #constAttribute maxConsumption {
            value2 :>> value default "23.0";
            :> dataType default AttributeDataType::DOUBLE;
        }
        #component sensor : PAC_Sensor;
    }

    abstract #Entity def IntermediateBattery :> AbstractEntity {
        #constAttribute :>> maxConsumption {
            :>> value2 default "10.0";
        }
    }

    abstract #Entity def Battery :> IntermediateBattery {
        #constAttribute :>> maxConsumption {
            :>> value2 default "5.0";
        }
        #component batterySensor :>> sensor;
        #component inverter : PAC_Sensor;
        part testNotIncuded;
    }

 
    #Twin def MGTwin {
        
        #entity MicroGrid {
            

            #entity battery : Battery {
                mComp :>> maxConsumption {
                    :>> value2 = "3.0";
                }
                
                internalInverter :> inverter; 
                
                test :> test;

                #component p12 :>> batterySensor;
            }

            #entity sieVercharge : AbstractEntity {
                #component p13 :>> sensor;
            }

            #entity kebaP30 : AbstractEntity {
                #constAttribute :>> maxConsumption {
                }
                #component p14 :>> sensor;
            }


            #entity edgeCaseNode : AbstractEntity {
               
            }
        }

        #condition CheckBatteryConsumption {
            :>> operator = ComparisonOperator::GREATER_THAN;
            
            :>> leftOperand  = MicroGrid.sieVercharge.p13.consumption;
        
            :>> rightOperand = MicroGrid.battery.mComp;
            #strategyAction alertAction {
                :>> name = "Alert Action";
                :>> strategyType = StrategyType::LAMBDA;
                :>> description = "Alerts when battery consumption is too high";
                :>> pathToCode = "\\path\\to\\alertFunction";
                :>> external = true;
                :>> feedbackTopicType = FeedbackTopicType::EXTERN;
                :>> externalTopic = "EXTERN_TPIC";
                :>> customPayload = "{\"message\":\"High Consumption Alert\"}";
            }

            #strategyAction alertAction2 {
                :>> name = "Internal Correction";
                :>> strategyType = StrategyType::LAMBDA;
                :>> description = "Feedback to battery sensor";
                :>> pathToCode = "";
                :>> external = false;
                :>> feedbackTopicType = FeedbackTopicType::INTERN;
                :>> componentTopic = MicroGrid.battery.p12;
            }

            #strategyAction alertAction3 {
                :>> name = "Log Action";
                :>> strategyType = StrategyType::LAMBDA;
                :>> external = false;
            }
        }
    }
}
```

#### Output: 
```json
//config_events.json
[
    {
        "condition": "mzd2dGWWdntbBdeCzpUZ8v.LcE4QQRx8bR5ZVBgghXbC6.NadbkxUDHw5EGM5Zzj5gWR > dZbP84rWQjLX6jSpAyxLdJ.dZbP84rWQjLX6jSpAyxLdJconst_component.nbugMpE4uNraZ3Ea8z2EoU",
        "action": {
            "type": "lambda",
            "pathToCode": "\\path\\to\\alertFunction",
            "functionName": "alertAction",
            "external": true,
            "feedback": {
                "type": "mqtt",
                "topic": "EXTERN_TPIC",
                "payload": {
                    "message": "High Consumption Alert"
                }
            }
        }
    },
    {
        "condition": "mzd2dGWWdntbBdeCzpUZ8v.LcE4QQRx8bR5ZVBgghXbC6.NadbkxUDHw5EGM5Zzj5gWR > dZbP84rWQjLX6jSpAyxLdJ.dZbP84rWQjLX6jSpAyxLdJconst_component.nbugMpE4uNraZ3Ea8z2EoU",
        "action": {
            "type": "lambda",
            "functionName": "alertAction2",
            "external": false,
            "feedback": {
                "type": "mqtt",
                "iotDeviceId": "GaNW7B2mByyNdMXN7BfzKn",
                "payload": "action-result"
            }
        }
    },
    {
        "condition": "mzd2dGWWdntbBdeCzpUZ8v.LcE4QQRx8bR5ZVBgghXbC6.NadbkxUDHw5EGM5Zzj5gWR > dZbP84rWQjLX6jSpAyxLdJ.dZbP84rWQjLX6jSpAyxLdJconst_component.nbugMpE4uNraZ3Ea8z2EoU",
        "action": {
            "type": "lambda",
            "functionName": "alertAction3",
            "external": false,
            "feedback": {
                "type": "mqtt",
                "payload": "action-result"
            }
        }
    }
]
//config.json
{
    "digital_twin_name": "MGTwin",
    "hot_storage_size_in_days": 30,
    "cold_storage_size_in_days": 30
}
//config_hierarchy.json
[
    {
        "id": "JftZFPj77VLDDaUnMCpsvn",
        "type": "entity",
        "name": "MicroGrid",
        "children": [
            {
                "id": "dZbP84rWQjLX6jSpAyxLdJ",
                "type": "entity",
                "name": "battery",
                "children": [
                    {
                        "iotDeviceId": "mdpAqdD7fMGNUMkK3QWAU2",
                        "type": "component",
                        "name": "internalInverter"
                    },
                    {
                        "iotDeviceId": "GaNW7B2mByyNdMXN7BfzKn",
                        "type": "component",
                        "name": "p12"
                    },
                    {
                        "iotDeviceId": "dZbP84rWQjLX6jSpAyxLdJconst_component",
                        "type": "component",
                        "name": "batteryconst_component"
                    }
                ]
            },
            {
                "id": "mzd2dGWWdntbBdeCzpUZ8v",
                "type": "entity",
                "name": "sieVercharge",
                "children": [
                    {
                        "iotDeviceId": "LcE4QQRx8bR5ZVBgghXbC6",
                        "type": "component",
                        "name": "p13"
                    },
                    {
                        "iotDeviceId": "mzd2dGWWdntbBdeCzpUZ8vconst_component",
                        "type": "component",
                        "name": "sieVerchargeconst_component"
                    }
                ]
            },
            {
                "id": "Bas34LaGXRk4CgFNDw8YWe",
                "type": "entity",
                "name": "kebaP30",
                "children": [
                    {
                        "iotDeviceId": "GCqPxSwMJcQFp9BHV4FDtZ",
                        "type": "component",
                        "name": "p14"
                    },
                    {
                        "iotDeviceId": "Bas34LaGXRk4CgFNDw8YWeconst_component",
                        "type": "component",
                        "name": "kebaP30const_component"
                    }
                ]
            },
            {
                "id": "NEG4C2iV7VoNpFRCsaw4Au",
                "type": "entity",
                "name": "edgeCaseNode",
                "children": [
                    {
                        "iotDeviceId": "PvK3LFTavuQtvtspuib3uq",
                        "type": "component",
                        "name": "sensor"
                    },
                    {
                        "iotDeviceId": "NEG4C2iV7VoNpFRCsaw4Auconst_component",
                        "type": "component",
                        "name": "edgeCaseNodeconst_component"
                    }
                ]
            }
        ]
    }
]
//config_iot_devices.json
[
    {
        "id": "mdpAqdD7fMGNUMkK3QWAU2",
        "properties": [
            {
                "name": "consumption",
                "dataType": "DOUBLE"
            }
        ]
    },
    {
        "id": "GaNW7B2mByyNdMXN7BfzKn",
        "properties": [
            {
                "name": "consumption",
                "dataType": "DOUBLE"
            }
        ]
    },
    {
        "id": "dZbP84rWQjLX6jSpAyxLdJconst_component",
        "properties": [
            {
                "name": "mComp",
                "dataType": "DOUBLE",
                "initValue": 3.0
            }
        ]
    },
    {
        "id": "LcE4QQRx8bR5ZVBgghXbC6",
        "properties": [
            {
                "name": "consumption",
                "dataType": "DOUBLE"
            }
        ]
    },
    {
        "id": "mzd2dGWWdntbBdeCzpUZ8vconst_component",
        "properties": [
            {
                "name": "maxConsumption",
                "dataType": "DOUBLE",
                "initValue": 23.0
            }
        ]
    },
    {
        "id": "GCqPxSwMJcQFp9BHV4FDtZ",
        "properties": [
            {
                "name": "consumption",
                "dataType": "DOUBLE"
            }
        ]
    },
    {
        "id": "Bas34LaGXRk4CgFNDw8YWeconst_component",
        "properties": [
            {
                "name": "maxConsumption",
                "dataType": "DOUBLE",
                "initValue": 23.0
            }
        ]
    },
    {
        "id": "PvK3LFTavuQtvtspuib3uq",
        "properties": [
            {
                "name": "consumption",
                "dataType": "DOUBLE"
            }
        ]
    },
    {
        "id": "NEG4C2iV7VoNpFRCsaw4Auconst_component",
        "properties": [
            {
                "name": "maxConsumption",
                "dataType": "DOUBLE",
                "initValue": 23.0
            }
        ]
    }
]
```
