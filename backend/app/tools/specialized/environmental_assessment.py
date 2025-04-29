from typing import Dict, List, Any, Optional
from app.tools.base_tool import ToolDefinition, ToolParameter
import asyncio

class SiteAnalysisTool(ToolDefinition):
    def __init__(self):
        super().__init__(
            name="site-analysis",
            description="Analyzes construction site characteristics and surrounding environment",
            category="environmental-assessment",
            input_schema={
                "location": ToolParameter(
                    type="object",
                    description="GPS coordinates or address of the construction site",
                    required=True
                ),
                "site_area": ToolParameter(
                    type="number",
                    description="Total area of the site in square meters",
                    required=True
                ),
                "terrain_type": ToolParameter(
                    type="string",
                    description="Type of terrain (flat, hilly, coastal, etc.)",
                    required=True
                ),
                "existing_vegetation": ToolParameter(
                    type="array",
                    description="List of existing vegetation types on site",
                    required=False
                )
            }
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        location = inputs["location"]
        site_area = inputs["site_area"]
        terrain_type = inputs["terrain_type"]
        existing_vegetation = inputs.get("existing_vegetation", [])
        
        # Simulate API delay
        await asyncio.sleep(1)
        
        # Generate environmental sensitivity rating based on inputs
        sensitivity = self._calculate_sensitivity(terrain_type, existing_vegetation, site_area)
        
        # Mock nearby water bodies based on location
        water_bodies = self._get_nearby_water_bodies(location)
        
        # Mock soil data based on terrain
        soil_data = self._get_soil_data(terrain_type)
        
        # Mock ecosystem data
        ecosystem_data = self._get_ecosystem_data(location, existing_vegetation)
        
        # Mock climate data
        climate_data = self._get_climate_data(location)
        
        return {
            "environmentalSensitivity": sensitivity,
            "nearbyWaterBodies": water_bodies,
            "soilComposition": soil_data,
            "localEcosystem": ecosystem_data,
            "climateFactors": climate_data
        }
    
    def _calculate_sensitivity(self, terrain_type: str, vegetation: List[str], area: float) -> str:
        """Calculate environmental sensitivity based on inputs"""
        # Simple scoring system
        score = 0
        
        # Terrain factors
        terrain_scores = {
            "flat": 1,
            "hilly": 2,
            "mountainous": 3,
            "coastal": 4,
            "wetland": 5
        }
        score += terrain_scores.get(terrain_type.lower(), 2)
        
        # Vegetation factors (more vegetation types = more sensitive)
        score += min(len(vegetation), 3)
        
        # Area factors (larger area = potentially more sensitive)
        if area > 10000:  # > 1 hectare
            score += 2
        elif area > 5000:
            score += 1
        
        # Convert score to rating
        if score >= 8:
            return "high"
        elif score >= 5:
            return "medium"
        else:
            return "low"
    
    def _get_nearby_water_bodies(self, location: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get nearby water bodies based on location"""
        # Mock data - in a real implementation, this would query GIS databases
        water_bodies_by_region = {
            "Seattle": [
                {"name": "Lake Washington", "distance": 1200, "type": "lake", "floodRisk": "low"},
                {"name": "Puget Sound", "distance": 3500, "type": "sound", "floodRisk": "low"}
            ],
            "Austin": [
                {"name": "Colorado River", "distance": 800, "type": "river", "floodRisk": "moderate"},
                {"name": "Lake Travis", "distance": 15000, "type": "lake", "floodRisk": "low"}
            ],
            "New York": [
                {"name": "Hudson River", "distance": 1500, "type": "river", "floodRisk": "moderate"},
                {"name": "East River", "distance": 2000, "type": "river", "floodRisk": "moderate"}
            ]
        }
        
        # Get city from location if available
        city = location.get("city", "")
        if city in water_bodies_by_region:
            return water_bodies_by_region[city]
        
        # Default mock water bodies
        return [
            {"name": "Small Creek", "distance": 450, "type": "creek", "floodRisk": "occasional"},
            {"name": "Unnamed Pond", "distance": 1200, "type": "pond", "floodRisk": "low"}
        ]
    
    def _get_soil_data(self, terrain_type: str) -> Dict[str, Any]:
        """Get soil data based on terrain type"""
        # Mock data based on terrain
        soil_types = {
            "flat": {
                "type": "alluvial",
                "permeability": "moderate to high",
                "erosionRisk": "low"
            },
            "hilly": {
                "type": "silty loam",
                "permeability": "moderate",
                "erosionRisk": "medium"
            },
            "mountainous": {
                "type": "rocky",
                "permeability": "low",
                "erosionRisk": "high"
            },
            "coastal": {
                "type": "sandy",
                "permeability": "high",
                "erosionRisk": "medium to high"
            },
            "wetland": {
                "type": "clay",
                "permeability": "low",
                "erosionRisk": "low"
            }
        }
        
        return soil_types.get(terrain_type.lower(), {
            "type": "mixed",
            "permeability": "moderate",
            "erosionRisk": "medium"
        })
    
    def _get_ecosystem_data(self, location: Dict[str, Any], vegetation: List[str]) -> Dict[str, Any]:
        """Get ecosystem data based on location and vegetation"""
        # Mock ecosystem types by region
        ecosystems_by_region = {
            "Seattle": {
                "habitatType": "temperate rainforest",
                "biodiversityIndex": 0.78,
                "protectedSpecies": ["Spotted Owl", "Coho Salmon"]
            },
            "Austin": {
                "habitatType": "mixed woodland/grassland",
                "biodiversityIndex": 0.72,
                "protectedSpecies": ["Golden-cheeked Warbler", "Black-capped Vireo"]
            },
            "New York": {
                "habitatType": "urban/suburban forest fragments",
                "biodiversityIndex": 0.45,
                "protectedSpecies": ["Peregrine Falcon"]
            }
        }
        
        # Get city from location if available
        city = location.get("city", "")
        if city in ecosystems_by_region:
            return ecosystems_by_region[city]
        
        # Default ecosystem data with adjustments based on vegetation
        habitat_type = "mixed woodland"
        if any("pine" in v.lower() for v in vegetation):
            habitat_type = "coniferous forest"
        elif any("oak" in v.lower() for v in vegetation):
            habitat_type = "deciduous forest"
        elif any("grass" in v.lower() for v in vegetation):
            habitat_type = "grassland"
            
        # Calculate biodiversity index based on vegetation diversity
        biodiversity = min(0.4 + (len(vegetation) * 0.1), 0.9)
        
        return {
            "habitatType": habitat_type,
            "biodiversityIndex": round(biodiversity, 2),
            "protectedSpecies": ["Local Protected Species"]
        }
    
    def _get_climate_data(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Get climate data based on location"""
        # Mock climate data by region
        climate_by_region = {
            "Seattle": {
                "annualRainfall": 950,
                "floodRisk": "medium",
                "windExposure": "moderate"
            },
            "Austin": {
                "annualRainfall": 870,
                "floodRisk": "medium",
                "windExposure": "low"
            },
            "New York": {
                "annualRainfall": 1200,
                "floodRisk": "medium to high",
                "windExposure": "moderate to high"
            }
        }
        
        # Get city from location if available
        city = location.get("city", "")
        if city in climate_by_region:
            return climate_by_region[city]
        
        # Default climate data
        return {
            "annualRainfall": 800,
            "floodRisk": "medium",
            "windExposure": "moderate"
        }

class RegulatoryComplianceTool(ToolDefinition):
    def __init__(self):
        super().__init__(
            name="regulatory-compliance",
            description="Identifies applicable environmental regulations and compliance requirements",
            category="environmental-assessment",
            input_schema={
                "project_location": ToolParameter(
                    type="object",
                    description="Project location with jurisdiction information",
                    required=True
                ),
                "project_type": ToolParameter(
                    type="string",
                    description="Type of construction project",
                    required=True
                ),
                "project_scale": ToolParameter(
                    type="string",
                    description="Scale of the project (small, medium, large)",
                    required=True
                ),
                "sensitive_elements": ToolParameter(
                    type="array",
                    description="List of environmentally sensitive elements",
                    required=False
                )
            }
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        project_location = inputs["project_location"]
        project_type = inputs["project_type"]
        project_scale = inputs["project_scale"]
        sensitive_elements = inputs.get("sensitive_elements", [])
        
        # Simulate API delay
        await asyncio.sleep(1.5)
        
        # Get regulations based on location
        location_regulations = self._get_location_regulations(project_location)
        
        # Get regulations based on project type
        project_regulations = self._get_project_regulations(project_type, project_scale)
        
        # Get regulations based on sensitive elements
        sensitivity_regulations = self._get_sensitivity_regulations(sensitive_elements)
        
        # Combine regulations
        all_regulations = location_regulations + project_regulations + sensitivity_regulations
        
        # Determine required assessments
        required_assessments = self._determine_required_assessments(all_regulations, sensitive_elements)
        
        # Estimate compliance timeline
        compliance_timeline = self._estimate_compliance_timeline(all_regulations, project_scale)
        
        # Determine mitigation requirements
        mitigation_requirements = self._determine_mitigation_requirements(all_regulations, sensitive_elements)
        
        return {
            "applicableRegulations": all_regulations,
            "requiredAssessments": required_assessments,
            "complianceTimeline": compliance_timeline,
            "mitigationRequirements": mitigation_requirements
        }
    
    def _get_location_regulations(self, location: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get regulations based on location"""
        # Mock data - in a real implementation, this would query a regulatory database
        regulations_by_region = {
            "USA": [
                {
                    "name": "Clean Water Act",
                    "jurisdiction": "Federal",
                    "applicability": "Activities affecting water bodies",
                    "permitRequired": True,
                    "authority": "EPA/Army Corps of Engineers"
                },
                {
                    "name": "Clean Air Act",
                    "jurisdiction": "Federal",
                    "applicability": "Air emissions during construction and operation",
                    "permitRequired": True,
                    "authority": "EPA"
                }
            ],
            "California": [
                {
                    "name": "California Environmental Quality Act (CEQA)",
                    "jurisdiction": "State",
                    "applicability": "All development projects",
                    "permitRequired": True,
                    "authority": "State and local agencies"
                }
            ],
            "Texas": [
                {
                    "name": "Edwards Aquifer Protection Program",
                    "jurisdiction": "State",
                    "applicability": "Development over Edwards Aquifer",
                    "permitRequired": True,
                    "authority": "Texas Commission on Environmental Quality"
                }
            ]
        }
        
        # Get country and state from location
        country = location.get("country", "")
        state = location.get("state", "")
        
        regulations = []
        
        if country in regulations_by_region:
            regulations.extend(regulations_by_region[country])
        
        if state in regulations_by_region:
            regulations.extend(regulations_by_region[state])
        
        return regulations
    
    def _get_project_regulations(self, project_type: str, project_scale: str) -> List[Dict[str, Any]]:
        """Get regulations based on project type and scale"""
        regulations = []
        
        # Building-specific regulations
        if "residential" in project_type.lower():
            regulations.append({
                "name": "Residential Building Energy Efficiency Standards",
                "jurisdiction": "Various",
                "applicability": "New residential construction",
                "permitRequired": True,
                "authority": "Local building department"
            })
        
        if "commercial" in project_type.lower():
            regulations.append({
                "name": "Commercial Building Standards",
                "jurisdiction": "Various",
                "applicability": "New commercial construction",
                "permitRequired": True,
                "authority": "Local building department"
            })
        
        # Scale-specific regulations
        if project_scale.lower() == "large":
            regulations.append({
                "name": "Environmental Impact Statement",
                "jurisdiction": "Federal",
                "applicability": "Large projects with significant environmental impact",
                "permitRequired": True,
                "authority": "Lead federal agency"
            })
        
        return regulations
    
    def _get_sensitivity_regulations(self, sensitive_elements: List[str]) -> List[Dict[str, Any]]:
        """Get regulations based on sensitive elements"""
        regulations = []
        
        for element in sensitive_elements:
            element_lower = element.lower()
            
            if "wetland" in element_lower or "water" in element_lower:
                regulations.append({
                    "name": "Section 404 Wetlands Permit",
                    "jurisdiction": "Federal",
                    "applicability": "Activities affecting wetlands",
                    "permitRequired": True,
                    "authority": "Army Corps of Engineers"
                })
            
            if "endangered" in element_lower or "species" in element_lower:
                regulations.append({
                    "name": "Endangered Species Act Consultation",
                    "jurisdiction": "Federal",
                    "applicability": "Activities affecting endangered species",
                    "permitRequired": True,
                    "authority": "US Fish and Wildlife Service"
                })
            
            if "tree" in element_lower or "forest" in element_lower:
                regulations.append({
                    "name": "Tree Preservation Ordinance",
                    "jurisdiction": "Local",
                    "applicability": "Removal of trees",
                    "permitRequired": True,
                    "authority": "Local planning department"
                })
        
        return regulations
    
    def _determine_required_assessments(self, regulations: List[Dict[str, Any]], 
                                      sensitive_elements: List[str]) -> List[str]:
        """Determine required environmental assessments"""
        assessments = set()
        
        # Based on regulations
        for regulation in regulations:
            reg_name = regulation["name"].lower()
            
            if "water" in reg_name or "wetland" in reg_name:
                assessments.add("Wetland Delineation")
                assessments.add("Water Quality Assessment")
            
            if "air" in reg_name:
                assessments.add("Air Quality Impact Assessment")
            
            if "species" in reg_name or "endangered" in reg_name:
                assessments.add("Biological Assessment")
            
            if "tree" in reg_name:
                assessments.add("Tree Survey")
            
            if "impact statement" in reg_name:
                assessments.add("Environmental Impact Statement")
        
        # Based on sensitive elements
        for element in sensitive_elements:
            element_lower = element.lower()
            
            if "wetland" in element_lower or "water" in element_lower:
                assessments.add("Wetland Delineation")
                assessments.add("Hydrological Assessment")
            
            if "species" in element_lower or "habitat" in element_lower:
                assessments.add("Biological Assessment")
                assessments.add("Habitat Evaluation")
            
            if "cultural" in element_lower or "historic" in element_lower:
                assessments.add("Cultural Resources Survey")
        
        return sorted(list(assessments))
    
    def _estimate_compliance_timeline(self, regulations: List[Dict[str, Any]], 
                                    project_scale: str) -> Dict[str, Any]:
        """Estimate compliance timeline"""
        # Base timeline estimates
        scale_factors = {
            "small": 1,
            "medium": 1.5,
            "large": 2.5
        }
        
        scale_factor = scale_factors.get(project_scale.lower(), 1)
        
        # Count permit requirements
        permits_required = sum(1 for reg in regulations if reg.get("permitRequired", False))
        
        # Calculate timeline
        base_time = 2  # months
        permit_time = permits_required * 1.5  # 1.5 months per permit
        
        estimated_time = (base_time + permit_time) * scale_factor
        
        # Determine critical path
        critical_paths = []
        if any("impact statement" in reg["name"].lower() for reg in regulations):
            critical_paths.append("Environmental Impact Statement")
        if any("endangered" in reg["name"].lower() for reg in regulations):
            critical_paths.append("Endangered Species Consultation")
        if not critical_paths:
            critical_paths.append("Standard Permitting Process")
        
        # Public comment periods
        public_comment_periods = []
        if any("impact statement" in reg["name"].lower() for reg in regulations):
            public_comment_periods.append("45-day public comment period for Environmental Impact Statement")
        if permits_required > 2:
            public_comment_periods.append("30-day public comment period for major permits")
        
        return {
            "estimatedPermittingTime": f"{int(estimated_time)}-{int(estimated_time + 2)} months",
            "criticalPath": critical_paths[0],
            "publicCommentPeriods": public_comment_periods
        }
    
    def _determine_mitigation_requirements(self, regulations: List[Dict[str, Any]], 
                                         sensitive_elements: List[str]) -> Dict[str, str]:
        """Determine mitigation requirements"""
        mitigation = {}
        
        # Based on regulations
        for regulation in regulations:
            reg_name = regulation["name"].lower()
            
            if "water" in reg_name or "wetland" in reg_name:
                mitigation["waterQuality"] = "Implement stormwater best management practices"
                if "wetland" in reg_name:
                    mitigation["wetlands"] = "Avoid wetland impacts or provide compensatory mitigation"
            
            if "air" in reg_name:
                mitigation["airQuality"] = "Dust control measures and low-emission equipment"
            
            if "species" in reg_name or "endangered" in reg_name:
                mitigation["biodiversity"] = "Habitat conservation measures and timing restrictions"
            
            if "tree" in reg_name:
                mitigation["vegetation"] = "Tree protection or replacement requirements"
        
        # Based on sensitive elements
        for element in sensitive_elements:
            element_lower = element.lower()
            
            if "flood" in element_lower:
                mitigation["floodProtection"] = "Elevate structures and implement flood control measures"
            
            if "noise" in element_lower:
                mitigation["noiseMitigation"] = "Install sound barriers and limit construction hours"
            
            if "cultural" in element_lower:
                mitigation["culturalResources"] = "Preserve cultural resources and implement monitoring"
        
        return mitigation

class AirQualityAssessmentTool(ToolDefinition):
    def __init__(self):
        super().__init__(
            name="air-quality-assessment",
            description="Assesses potential air quality impacts from construction and operation activities",
            category="environmental-assessment",
            input_schema={
                "project_location": ToolParameter(
                    type="object",
                    description="GPS coordinates or location details of the project",
                    required=True
                ),
                "project_activities": ToolParameter(
                    type="array",
                    description="List of activities that may impact air quality",
                    required=True
                ),
                "local_air_quality_baseline": ToolParameter(
                    type="string",
                    description="Baseline air quality in the project area",
                    required=True
                ),
                "mitigation_measures": ToolParameter(
                    type="array",
                    description="Proposed measures to mitigate air quality impacts",
                    required=False
                )
            }
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        location = inputs["project_location"]
        activities = inputs["project_activities"]
        baseline = inputs["local_air_quality_baseline"]
        mitigation = inputs.get("mitigation_measures", [])
        
        # Simulate API delay
        await asyncio.sleep(1)
        
        # Calculate impact levels based on inputs
        construction_impact = self._calculate_construction_impact(activities, baseline)
        operational_impact = self._calculate_operational_impact(activities, baseline)
        
        # Assess effectiveness of mitigation measures
        mitigation_effectiveness = self._assess_mitigation(mitigation, construction_impact, operational_impact)
        
        # Generate recommended additional measures if needed
        additional_measures = []
        if construction_impact > 2 and "dust suppression" not in mitigation:
            additional_measures.append("Implement dust suppression with water spraying during dry conditions")
        if "vehicle emissions" in activities and "use of low-emission vehicles" not in mitigation:
            additional_measures.append("Require use of low-emission or electric construction vehicles")
        if construction_impact > 3:
            additional_measures.append("Monitor air quality during construction and adjust methods if thresholds exceeded")
        
        return {
            "constructionImpact": {
                "level": self._impact_level_name(construction_impact),
                "description": self._get_construction_impact_description(construction_impact, activities)
            },
            "operationalImpact": {
                "level": self._impact_level_name(operational_impact),
                "description": self._get_operational_impact_description(operational_impact, activities)
            },
            "mitigationEffectiveness": mitigation_effectiveness,
            "recommendedAdditionalMeasures": additional_measures,
            "complianceStatus": "Compliant with local regulations" if (construction_impact - mitigation_effectiveness / 2) < 3 else "Additional mitigation required"
        }
    
    def _calculate_construction_impact(self, activities: List[str], baseline: str) -> int:
        """Calculate construction phase air quality impact on a scale of 1-5"""
        impact = 0
        
        # Base impact level based on baseline
        if baseline.lower() == "poor":
            impact += 2
        elif baseline.lower() == "moderate":
            impact += 1
        
        # Add impact based on activities
        if "excavation" in [a.lower() for a in activities]:
            impact += 1
        if "grading" in [a.lower() for a in activities]:
            impact += 1
        if "demolition" in [a.lower() for a in activities]:
            impact += 2
        if "blasting" in [a.lower() for a in activities]:
            impact += 2
        
        # Cap impact at 5
        return min(impact + 1, 5)
    
    def _calculate_operational_impact(self, activities: List[str], baseline: str) -> int:
        """Calculate operational phase air quality impact on a scale of 1-5"""
        impact = 0
        
        # Base impact level based on baseline
        if baseline.lower() == "poor":
            impact += 1
        
        # Add impact based on activities
        if "vehicle emissions" in [a.lower() for a in activities]:
            impact += 1
        if "hvac operations" in [a.lower() for a in activities]:
            impact += 1
        if "industrial processes" in [a.lower() for a in activities]:
            impact += 2
        
        # Cap impact at 5
        return min(impact + 1, 5)
    
    def _assess_mitigation(self, mitigation: List[str], construction_impact: int, operational_impact: int) -> Dict[str, Any]:
        """Assess the effectiveness of mitigation measures"""
        effectiveness = 0
        
        for measure in mitigation:
            measure_lower = measure.lower()
            if "dust" in measure_lower:
                effectiveness += 1
            if "emission" in measure_lower:
                effectiveness += 1
            if "monitor" in measure_lower:
                effectiveness += 0.5
            if "electric" in measure_lower:
                effectiveness += 1.5
        
        percentage = min(effectiveness / max(construction_impact, operational_impact) * 100, 95)
        
        return {
            "score": round(percentage, 1),
            "assessment": "High" if percentage > 75 else "Moderate" if percentage > 50 else "Low"
        }
    
    def _impact_level_name(self, impact: int) -> str:
        """Convert numeric impact level to name"""
        levels = {
            1: "Negligible",
            2: "Minor",
            3: "Moderate",
            4: "Significant",
            5: "Severe"
        }
        return levels.get(impact, "Unknown")
    
    def _get_construction_impact_description(self, impact: int, activities: List[str]) -> str:
        """Generate a description of construction impacts"""
        if impact <= 2:
            return f"Limited impact from {', '.join(activities[:2])} with temporary, localized effects on air quality."
        elif impact <= 3:
            return f"Moderate dust and emissions from {', '.join(activities[:2])} with potential to affect nearby sensitive receptors."
        else:
            return f"Significant air quality degradation from {', '.join(activities[:2])} with substantial emissions that could affect surrounding areas."
    
    def _get_operational_impact_description(self, impact: int, activities: List[str]) -> str:
        """Generate a description of operational impacts"""
        if impact <= 2:
            return "Minimal ongoing air quality impacts during normal operations."
        elif impact <= 3:
            return "Moderate emissions from regular operations that contribute to local air quality concerns."
        else:
            return "Significant ongoing air quality impacts that could contribute to regulatory exceedances without proper mitigation."

class HydrologicalAssessmentTool(ToolDefinition):
    def __init__(self):
        super().__init__(
            name="hydrological-assessment",
            description="Assesses potential impacts on water flow, drainage patterns, and groundwater",
            category="environmental-assessment",
            input_schema={
                "project_location": ToolParameter(
                    type="object",
                    description="GPS coordinates or location details of the project",
                    required=True
                ),
                "site_area": ToolParameter(
                    type="number",
                    description="Total area of the site in square meters",
                    required=True
                ),
                "soil_type": ToolParameter(
                    type="string",
                    description="Type of soil at the site",
                    required=True
                ),
                "soil_permeability": ToolParameter(
                    type="string",
                    description="Permeability of the soil",
                    required=True
                ),
                "nearby_water_bodies": ToolParameter(
                    type="array",
                    description="List of water bodies near the project site",
                    required=True
                ),
                "proposed_mitigation": ToolParameter(
                    type="array",
                    description="Proposed measures to mitigate hydrological impacts",
                    required=False
                )
            }
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        location = inputs["project_location"]
        site_area = inputs["site_area"]
        soil_type = inputs["soil_type"]
        soil_permeability = inputs["soil_permeability"]
        water_bodies = inputs["nearby_water_bodies"]
        mitigation = inputs.get("proposed_mitigation", [])
        
        # Simulate API delay
        await asyncio.sleep(1)
        
        # Calculate impervious surface increase
        impervious_surface = self._calculate_impervious_surface(site_area)
        
        # Calculate runoff increase
        runoff_increase = self._calculate_runoff_increase(site_area, impervious_surface, soil_permeability)
        
        # Assess infiltration reduction
        infiltration_reduction = self._assess_infiltration_reduction(soil_type, soil_permeability, impervious_surface)
        
        # Assess flood risk change
        flood_risk = self._assess_flood_risk(water_bodies, runoff_increase, location)
        
        # Assess effectiveness of mitigation measures
        mitigation_effectiveness = self._assess_mitigation(mitigation, runoff_increase, infiltration_reduction)
        
        # Generate recommended additional measures if needed
        additional_measures = []
        if runoff_increase > 30 and not any("permeable" in m.lower() for m in mitigation):
            additional_measures.append("Use permeable paving materials for parking areas")
        if runoff_increase > 20 and not any("retention" in m.lower() for m in mitigation):
            additional_measures.append("Install stormwater retention basins")
        if flood_risk["level"] == "High" and not any("floodplain" in m.lower() for m in mitigation):
            additional_measures.append("Relocate critical facilities outside floodplain areas")
        
        return {
            "imperviousSurfaceIncrease": {
                "percentage": round(impervious_surface, 1),
                "area": round(site_area * impervious_surface / 100, 1)
            },
            "runoffIncrease": {
                "percentage": round(runoff_increase, 1),
                "impact": "High" if runoff_increase > 30 else "Moderate" if runoff_increase > 15 else "Low"
            },
            "infiltrationReduction": {
                "percentage": round(infiltration_reduction, 1),
                "impact": "High" if infiltration_reduction > 30 else "Moderate" if infiltration_reduction > 15 else "Low"
            },
            "floodRisk": flood_risk,
            "mitigationEffectiveness": mitigation_effectiveness,
            "recommendedAdditionalMeasures": additional_measures
        }
    
    def _calculate_impervious_surface(self, site_area: float) -> float:
        """Calculate expected percentage of impervious surface based on site size"""
        # Simple formula assuming larger sites have proportionally less impervious surface
        base_impervious = 65  # Base percentage for commercial development
        
        # Adjust based on site size (acres converted from m²)
        acres = site_area / 4046.86
        if acres > 5:
            reduction_factor = 0.15  # 15% reduction for large sites
        elif acres > 2:
            reduction_factor = 0.1   # 10% reduction for medium sites
        elif acres > 1:
            reduction_factor = 0.05  # 5% reduction for small-medium sites
        else:
            reduction_factor = 0     # No reduction for small sites
            
        return base_impervious * (1 - reduction_factor)
    
    def _calculate_runoff_increase(self, site_area: float, impervious_percentage: float, soil_permeability: str) -> float:
        """Calculate expected increase in runoff"""
        # Base runoff increase based on impervious surface percentage
        runoff_base = impervious_percentage * 0.6
        
        # Adjust based on soil permeability
        permeability_factor = 1.0
        if "high" in soil_permeability.lower():
            permeability_factor = 0.8
        elif "moderate" in soil_permeability.lower():
            permeability_factor = 1.0
        elif "low" in soil_permeability.lower():
            permeability_factor = 1.2
            
        return runoff_base * permeability_factor
    
    def _assess_infiltration_reduction(self, soil_type: str, soil_permeability: str, impervious_percentage: float) -> float:
        """Assess reduction in infiltration"""
        # Base reduction is related to impervious percentage
        infiltration_reduction = impervious_percentage * 0.5
        
        # Adjust based on soil type and permeability
        if "clay" in soil_type.lower() or "low" in soil_permeability.lower():
            infiltration_reduction *= 0.8  # Less impact as infiltration already low
        elif "sandy" in soil_type.lower() or "high" in soil_permeability.lower():
            infiltration_reduction *= 1.2  # More impact as infiltration was high
            
        return infiltration_reduction
    
    def _assess_flood_risk(self, water_bodies: List[str], runoff_increase: float, location: Dict[str, Any]) -> Dict[str, Any]:
        """Assess flood risk based on nearby water bodies and runoff increase"""
        # Start with a base risk
        base_risk = 1.0
        
        # Increase risk based on water body types
        for body in water_bodies:
            body_lower = body.lower()
            if "river" in body_lower:
                base_risk += 0.5
            if "creek" in body_lower:
                base_risk += 0.3
            if "wetland" in body_lower:
                base_risk += 0.4
            if "pond" in body_lower:
                base_risk += 0.2
                
        # Adjust risk based on runoff increase
        risk_factor = base_risk * (1 + runoff_increase / 100)
        
        # Determine risk level
        if risk_factor > 2.5:
            risk_level = "High"
            description = "Significant potential for increased flooding, especially during heavy precipitation events."
        elif risk_factor > 1.5:
            risk_level = "Moderate"
            description = "Some increase in flood potential, primarily during severe weather events."
        else:
            risk_level = "Low"
            description = "Minimal change to existing flood patterns expected."
            
        return {
            "level": risk_level,
            "description": description,
            "riskFactor": round(risk_factor, 2)
        }
    
    def _assess_mitigation(self, mitigation: List[str], runoff_increase: float, infiltration_reduction: float) -> Dict[str, Any]:
        """Assess the effectiveness of mitigation measures"""
        effectiveness = 0
        max_potential_issues = runoff_increase + infiltration_reduction
        
        for measure in mitigation:
            measure_lower = measure.lower()
            if "retention" in measure_lower or "detention" in measure_lower:
                effectiveness += 15
            if "permeable" in measure_lower or "pervious" in measure_lower:
                effectiveness += 10
            if "swale" in measure_lower or "bioswale" in measure_lower:
                effectiveness += 8
            if "erosion" in measure_lower:
                effectiveness += 5
            if "drainage" in measure_lower:
                effectiveness += 7
                
        percentage = min(effectiveness / max_potential_issues * 100, 95)
        
        return {
            "score": round(percentage, 1),
            "assessment": "High" if percentage > 70 else "Moderate" if percentage > 40 else "Low"
        }

class WaterQualityAssessmentTool(ToolDefinition):
    def __init__(self):
        super().__init__(
            name="water-quality-assessment",
            description="Assesses potential impacts on water quality in nearby water bodies",
            category="environmental-assessment",
            input_schema={
                "project_location": ToolParameter(
                    type="object",
                    description="GPS coordinates or location details of the project",
                    required=True
                ),
                "nearby_water_bodies": ToolParameter(
                    type="array",
                    description="List of water bodies near the project site",
                    required=True
                ),
                "potential_contaminants": ToolParameter(
                    type="array",
                    description="List of potential contaminants from the project",
                    required=True
                ),
                "proposed_mitigation": ToolParameter(
                    type="array",
                    description="Proposed measures to mitigate water quality impacts",
                    required=False
                )
            }
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        location = inputs["project_location"]
        water_bodies = inputs["nearby_water_bodies"]
        contaminants = inputs["potential_contaminants"]
        mitigation = inputs.get("proposed_mitigation", [])
        
        # Simulate API delay
        await asyncio.sleep(1)
        
        # Assess impacts on each water body
        water_body_impacts = []
        for body in water_bodies:
            impact = self._assess_water_body_impact(body, contaminants)
            water_body_impacts.append({
                "name": body,
                "impact": impact
            })
        
        # Assess overall severity
        overall_severity = self._calculate_overall_severity(water_body_impacts)
        
        # Assess contaminant risks
        contaminant_risks = self._assess_contaminant_risks(contaminants)
        
        # Assess mitigation effectiveness
        mitigation_effectiveness = self._assess_mitigation(mitigation, contaminants, overall_severity)
        
        # Generate recommended additional measures
        additional_measures = []
        if overall_severity > 3 and not any("monitoring" in m.lower() for m in mitigation):
            additional_measures.append("Implement regular water quality monitoring program")
        if any(c in ["oil", "grease", "fuel"] for c in contaminants) and not any("separator" in m.lower() for m in mitigation):
            additional_measures.append("Install oil-water separators for stormwater runoff from parking areas")
        if any(c in ["sediment", "soil"] for c in contaminants) and not any("sediment" in m.lower() for m in mitigation):
            additional_measures.append("Install sediment traps and silt fences during construction")
        
        return {
            "waterBodyImpacts": water_body_impacts,
            "overallImpactSeverity": {
                "level": self._severity_level_name(overall_severity),
                "score": overall_severity
            },
            "contaminantRisks": contaminant_risks,
            "mitigationEffectiveness": mitigation_effectiveness,
            "recommendedAdditionalMeasures": additional_measures,
            "regulatoryConsiderations": self._get_regulatory_considerations(contaminants, water_bodies)
        }
    
    def _assess_water_body_impact(self, water_body: str, contaminants: List[str]) -> Dict[str, Any]:
        """Assess impact on a specific water body"""
        body_lower = water_body.lower()
        
        # Set base sensitivity based on water body type
        sensitivity = 2  # Default moderate sensitivity
        if "wetland" in body_lower:
            sensitivity = 4  # High sensitivity
        elif "river" in body_lower or "stream" in body_lower:
            sensitivity = 3  # Moderate-high sensitivity
        elif "pond" in body_lower or "lake" in body_lower:
            sensitivity = 3  # Moderate-high sensitivity
        
        # Calculate impact based on contaminants
        impact_score = 0
        for contaminant in contaminants:
            if contaminant.lower() in ["sediment", "soil"]:
                impact_score += 2
            elif contaminant.lower() in ["oil", "grease", "fuel"]:
                impact_score += 3
            elif contaminant.lower() in ["fertilizers", "nutrients"]:
                impact_score += 2.5
            elif contaminant.lower() in ["chemicals", "solvents"]:
                impact_score += 3.5
            else:
                impact_score += 1
        
        # Average and scale by sensitivity
        avg_impact = (impact_score / len(contaminants)) * (sensitivity / 3)
        
        # Determine impact level
        if avg_impact > 3:
            impact_level = "High"
            description = f"Significant risk to water quality in {water_body}, particularly from {', '.join(contaminants[:2])}"
        elif avg_impact > 2:
            impact_level = "Moderate"
            description = f"Moderate risks to water quality in {water_body}, monitoring recommended"
        else:
            impact_level = "Low"
            description = f"Limited impact expected on {water_body} with proper controls in place"
            
        return {
            "level": impact_level,
            "description": description,
            "score": round(avg_impact, 1)
        }
    
    def _calculate_overall_severity(self, water_body_impacts: List[Dict[str, Any]]) -> float:
        """Calculate the overall severity of water quality impacts"""
        if not water_body_impacts:
            return 1.0
            
        # Use the highest individual impact score as a base
        max_score = max(impact["impact"]["score"] for impact in water_body_impacts)
        
        # Average with the mean of all scores to account for multiple impacts
        mean_score = sum(impact["impact"]["score"] for impact in water_body_impacts) / len(water_body_impacts)
        
        return (max_score * 0.7) + (mean_score * 0.3)
    
    def _assess_contaminant_risks(self, contaminants: List[str]) -> List[Dict[str, Any]]:
        """Assess risks associated with specific contaminants"""
        risk_assessments = []
        
        for contaminant in contaminants:
            if contaminant.lower() in ["sediment", "soil"]:
                risk_assessments.append({
                    "contaminant": contaminant,
                    "risk": "Increased turbidity, reduced oxygen levels, habitat degradation",
                    "severity": "Moderate",
                    "treatmentOptions": ["Sediment basins", "Silt fences", "Erosion control blankets"]
                })
            elif contaminant.lower() in ["oil", "grease", "fuel"]:
                risk_assessments.append({
                    "contaminant": contaminant,
                    "risk": "Surface film, aquatic toxicity, long-term contamination",
                    "severity": "High",
                    "treatmentOptions": ["Oil-water separators", "Absorbent booms", "Bioremediation"]
                })
            elif contaminant.lower() in ["fertilizers", "nutrients"]:
                risk_assessments.append({
                    "contaminant": contaminant,
                    "risk": "Algal blooms, eutrophication, dissolved oxygen depletion",
                    "severity": "Moderate-High",
                    "treatmentOptions": ["Nutrient management plans", "Vegetative buffers", "Wetland treatment"]
                })
            elif contaminant.lower() in ["chemicals", "solvents", "construction chemicals"]:
                risk_assessments.append({
                    "contaminant": contaminant,
                    "risk": "Acute toxicity to aquatic life, bioaccumulation, water supply impacts",
                    "severity": "High",
                    "treatmentOptions": ["Secure storage", "Spill prevention plans", "Chemical treatment systems"]
                })
            else:
                risk_assessments.append({
                    "contaminant": contaminant,
                    "risk": "General water quality degradation",
                    "severity": "Low-Moderate",
                    "treatmentOptions": ["Best management practices", "Stormwater treatment"]
                })
                
        return risk_assessments
    
    def _assess_mitigation(self, mitigation: List[str], contaminants: List[str], severity: float) -> Dict[str, Any]:
        """Assess the effectiveness of mitigation measures"""
        effectiveness = 0
        relevant_measures = 0
        
        for measure in mitigation:
            measure_lower = measure.lower()
            relevant = False
            
            if "erosion" in measure_lower and any(c.lower() in ["sediment", "soil"] for c in contaminants):
                effectiveness += 3
                relevant = True
            if "stormwater" in measure_lower:
                effectiveness += 2.5
                relevant = True
            if "oil" in measure_lower and any(c.lower() in ["oil", "grease", "fuel"] for c in contaminants):
                effectiveness += 3
                relevant = True
            if "monitoring" in measure_lower:
                effectiveness += 1
                relevant = True
            if "buffer" in measure_lower:
                effectiveness += 2
                relevant = True
                
            if relevant:
                relevant_measures += 1
                
        # If no relevant measures found, return low effectiveness
        if relevant_measures == 0:
            return {
                "score": 20.0,
                "assessment": "Low",
                "gaps": "No specific water quality protection measures identified"
            }
            
        percentage = min((effectiveness / (severity * 2)) * 100, 95)
        
        gaps = []
        if percentage < 50:
            if any(c.lower() in ["sediment", "soil"] for c in contaminants) and not any("erosion" in m.lower() for m in mitigation):
                gaps.append("Erosion and sediment control")
            if any(c.lower() in ["oil", "grease", "fuel"] for c in contaminants) and not any("oil" in m.lower() for m in mitigation):
                gaps.append("Oil and grease management")
            if not any("monitor" in m.lower() for m in mitigation):
                gaps.append("Water quality monitoring")
        
        return {
            "score": round(percentage, 1),
            "assessment": "High" if percentage > 70 else "Moderate" if percentage > 40 else "Low",
            "gaps": ", ".join(gaps) if gaps else "None identified"
        }
    
    def _severity_level_name(self, severity: float) -> str:
        """Convert numeric severity to level name"""
        if severity > 3.5:
            return "Very High"
        elif severity > 2.5:
            return "High"
        elif severity > 1.5:
            return "Moderate"
        else:
            return "Low"
    
    def _get_regulatory_considerations(self, contaminants: List[str], water_bodies: List[str]) -> List[str]:
        """Identify relevant regulatory considerations"""
        regulations = ["Clean Water Act - National Pollutant Discharge Elimination System (NPDES) permit requirements"]
        
        if any(c.lower() in ["oil", "fuel"] for c in contaminants):
            regulations.append("Spill Prevention, Control, and Countermeasure (SPCC) regulations")
            
        if any("wetland" in body.lower() for body in water_bodies):
            regulations.append("Clean Water Act Section 404 Wetlands Protection")
            
        if "groundwater" in " ".join(water_bodies).lower():
            regulations.append("Safe Drinking Water Act - potential groundwater impacts")
            
        return regulations 