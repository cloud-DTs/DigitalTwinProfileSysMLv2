package MetaModelDigitalTwin {

    private import DigitalTwinLibrary::*;
    private import Metaobjects::SemanticMetadata;
    public import DigitalTwinLibrary::AttributeDataType;
    public import DigitalTwinLibrary::MeasurementInterfaceType;
    metadata def Twin specializes SemanticMetadata {
        redefines baseType = LibTwin meta SysML::PartDefinition;
        subsets annotatedElement : SysML::Definition;
        
    }

    metadata def Entity specializes SemanticMetadata{
        redefines baseType = LibTwinEntity meta SysML::PartDefinition;
        subsets annotatedElement : SysML::Definition;
    }

    metadata def entity specializes SemanticMetadata{
        redefines baseType = libTwinEntities meta SysML::PartUsage;
        subsets annotatedElement : SysML::Usage;
    }
    
    metadata def Component specializes SemanticMetadata{
        redefines baseType = LibTwinComponent meta SysML::PartDefinition;
        subsets annotatedElement : SysML::Definition;
    }

    metadata def component specializes SemanticMetadata{
        redefines baseType = cmponents meta SysML::PartUsage;
        subsets annotatedElement : SysML::Usage;
    }

    metadata def DataBase specializes SemanticMetadata{
        redefines baseType =LibTwinDataBase meta SysML::PartDefinition;
        subsets annotatedElement : SysML::Definition;
    }

    metadata def database specializes SemanticMetadata{
        redefines baseType = dataBases meta SysML::PartUsage;
        subsets annotatedElement : SysML::Usage;
    }

    metadata def MeasureInterface specializes SemanticMetadata{
        redefines baseType=MeasurementInterface meta SysML::InterfaceDefinition;
        subsets annotatedElement : SysML::InterfaceDefinition;
    }

    metadata def measureInterface specializes SemanticMetadata{
        redefines baseType=measurementInterfaces meta SysML::InterfaceUsage;
        subsets annotatedElement : SysML::Usage;
    }

    metadata def Measurement specializes SemanticMetadata{
        redefines baseType=MeasurePort meta SysML::PortDefinition;
        subsets annotatedElement : SysML::Definition;
        subsets annotatedElement : MeasureInterface; 
    }

    metadata def measure specializes SemanticMetadata{
        redefines baseType=measurements meta SysML::PortUsage;
        subsets annotatedElement : SysML::Usage;
    }

    metadata def ConstAttribute specializes SemanticMetadata{
        redefines baseType=ConstAttributes meta SysML::AttributeDefinition;
        subsets annotatedElement : SysML::Definition;
    }

    metadata def MeasureAttribute specializes SemanticMetadata{
        redefines baseType=LibDTAttributes meta SysML::AttributeDefinition;
        subsets annotatedElement : SysML::Definition;
    }

    metadata def constAttribute specializes SemanticMetadata{
        redefines baseType=const_attributes meta SysML::AttributeUsage;
        subsets annotatedElement : SysML::Usage;
    }

    metadata def measureAttribute specializes SemanticMetadata{
        redefines baseType=measurement meta SysML::AttributeUsage;
        subsets annotatedElement : SysML::Usage;
    }

    metadata def Condition specializes SemanticMetadata{
        redefines baseType=LibTwinConditionAction meta SysML::ActionDefinition;
        subsets annotatedElement:SysML::Definition;
    }
   


}