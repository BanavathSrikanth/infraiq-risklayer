# RiskLayer Domain and Workflow Model

## Product boundary

RiskLayer connects:

**Data -> Condition -> Risk -> Prioritization -> Recommendation -> Decision -> Work -> Verification -> Risk Reduction -> Continued Monitoring**

The platform is not an inspection-only application, GIS viewer, work-order system, or black-box risk score. Those capabilities are different views and stages of one continuing asset history.

## Authoritative domain concepts

These concepts must remain separate in the architecture, APIs, persistence model, and user experience:

| Concept | Meaning | Owns |
| --- | --- | --- |
| Asset | Physical infrastructure | Stable identity, lifecycle, location, components, and relationships |
| Condition | Observed state of an asset or related environment | Observation, measurement, inspection context, timestamp, and evidence |
| Finding / Issue | Something identified that may require attention | Defect or issue description, severity, evidence, status, and source condition |
| Risk | Evaluated exposure, likelihood, and consequence associated with a condition | Risk factors, score, drivers, evaluation version, confidence, and evaluation history |
| Recommendation | Proposed response to a risk | Treatment proposal, rationale, expected benefit, priority, and provenance |
| Decision | Authorized selection, rejection, modification, acceptance, or deferral | Decision outcome, authority, rationale, conditions, and audit history |
| Work Order / Action | Executable mitigation activity | Scope, owner, contractor, schedule, cost, and execution status |
| Completion | Report that work was performed | Performed scope, dates, evidence, cost, and submitter |
| Verification | Authorized confirmation that work meets requirements | Reviewer, criteria, evidence, result, and verification date |
| Residual Risk | Risk remaining after treatment | Post-treatment evaluation, comparison to prior risk, and acceptance/monitoring requirement |

These are not interchangeable and must not be represented by one generic `status` field. Each concept may have its own lifecycle/status, but statuses must describe that concept only.

### Ownership and routing

RiskLayer keeps risk responsibility separate from execution responsibility:

- **Risk Owner**: the person/team responsible for understanding, reviewing, and monitoring the risk, such as a Risk & Resilience Analyst.
- **Work Owner**: the operational manager responsible for arranging the mitigation response, such as a Vegetation Manager or Maintenance Manager.
- **Performer**: the crew or contractor that executes the work.
- **Verifier**: the authorized person who confirms the work meets requirements.

`RiskRouting` records who routed a risk and to which team/role. `WorkAssignment` records who assigned the resulting work and to whom. Routing never silently creates a work assignment unless an explicitly configured and approved automatic business rule permits it.

For consequential decisions such as pole replacement, the normal path is:

**Inspection / Data -> Risk Evaluation -> Risk Owner Review -> Engineering Analysis -> Financial / Program Review -> Authorized Decision -> Work Assignment -> Execution -> Verification -> Re-score -> Monitor**

Repair, reinforce, replace, monitor, and defer are decision alternatives. Approval authority and financial thresholds are tenant-configurable.

## AI boundary

AI is an always-available assistive capability for extraction, classification, relationship discovery, retrieval, evaluation support, and recommendation generation. AI output is never authoritative by default.

Every AI result must be represented as a proposal with:

- a stable proposal identifier
- the target concept and referenced asset/history records
- source references and evidence excerpts where available
- confidence and uncertainty
- provider, model, model version, prompt, and prompt version
- generated timestamp
- `authoritative: false`
- a proposal lifecycle such as `proposed`, `approved`, `rejected`, or `superseded`
- reviewer and review timestamp when a user acts on it

Approval or rejection of an AI proposal is a decision/action in the domain layer. Approving a proposal does not silently turn unrelated AI output into authoritative data; the owning service must validate it and create or update the appropriate domain record.

## One asset, one continuing history

An asset keeps one stable identity across departments and workflows. The platform links all relevant records to that asset rather than creating a new asset record as work moves:

- asset information and components
- conditions, inspections, photographs, and other evidence
- findings and defects
- vegetation relationships and environmental exposure
- weather events
- risk evaluations and risk-score history
- recommendations, decisions, and approvals
- work orders, actions, costs, and contractors
- completion evidence and verification
- residual risk and compliance history

Historical records should be append-only or versioned where practical. Re-scoring creates a new risk evaluation linked to its inputs and prior evaluation; it does not overwrite the risk history.

### Immutable source and calculation history

Dynamic hazard monitoring (DHM) uses live or time-varying weather data. Every calculation captures an immutable source snapshot, including the weather observation timestamp, source identifier, complete calculation input payload, calculation timestamp, calculation version, and a unique source event/evaluation identifier. A later DHM calculation creates another record; it never edits the previous weather input, score, or explanation.

The latest-risk view is only a convenience projection. It is not the source of truth and must never be used to replace or mutate history. Source observations and historical evaluations are append-only. Corrections are represented by a new source event linked to the prior record, not by updating the original.

## Branching workflows

The nine stages are a framework, not a mandatory department sequence. Workflow routing is driven by condition type, risk drivers, confidence, policy, and decision authority.

Example routes:

- **Vegetation issue:** Detection -> QA/QC -> Risk Evaluation -> Vegetation Management -> Work -> Verification -> Re-score -> Monitor
- **Structural pole issue:** Inspection -> QA/QC -> Risk Evaluation -> Engineering -> Decision -> Work -> Verification -> Re-score -> Monitor
- **Missing information:** Risk Evaluation -> Additional Inspection -> QA/QC -> Re-evaluate Risk
- **No immediate treatment:** Risk Evaluation -> Monitor -> Scheduled Re-evaluation

Workflow instances should reference the asset and the relevant condition, finding, risk evaluation, recommendation, decision, and action. A workflow status must not replace the lifecycle status of those records.

## Broadened system scope

RiskLayer is not just a field or inspection product. It is a risk-operating platform spanning data acquisition, condition recognition, spatial hazard context, asset consequence analysis, work execution, and residual-risk monitoring.

The platform needs to support these distinct but connected layers:

- **Source data layer**: asset registry, maintenance history, weather, GIS, vegetation, LiDAR, imagery, outage data, customer consequence, and third-party hazard feeds
- **Condition and evidence layer**: inspections, defects, field observations, photographs, GPS, telemetry, and supporting documentation
- **Risk layer**: condition, exposure, consequence, likelihood, confidence, drivers, score history, and residual risk
- **Work layer**: recommendations, decisions, assignments, completions, verifications, and contractor evidence
- **Portfolio layer**: trends, program-level prioritization, deferred risk, cost-benefit, and executive reporting
- **Operational layer**: offline sync, assignment queues, device state, team roles, and workflow transitions

### System-of-record versus projection model

The architecture should enforce a clear split between system-of-record data and derived projections:

- **System of record**: authoritative asset identities, conditions, findings, decisions, work orders, verification records, and immutable calculation inputs/history
- **Derived projections**: map overlays, priority views, dashboards, risk rollups, portfolio summaries, role-specific lists, and AI-generated recommendations

Derived views may be recomputed at any time, but they must never overwrite the authoritative record or replace the event history.

### Calculation and event history model

Every material calculation or system action must record:

- a stable event or evaluation identifier
- timestamp of the event
- timestamp the source data was observed
- source identifier and source type
- ingestion or retrieval method
- full input payload or input snapshot
- calculation version / model version / rule version
- output result and confidence
- linked prior result if this is a versioned update

This applies to:

- live weather or DHM evaluation
- risk score recalculation
- vegetation clearance or strike-risk evaluation
- exposure overlays related to flood, fire, wind, or heat
- pole prioritization or work-ranking calculations
- verification and residual-risk updates

A new calculation is a new record. It does not replace the previous source or prior score.

## Service ownership

The existing service boundaries map to the model as follows:

- `asset-service`: Asset identity, components, and asset relationships
- `inspection-service`: Conditions, inspections, field observations, and inspection context
- `evidence-document-service`: Photographs, documents, completion evidence, and provenance
- `risk-service`: Risk evaluations, drivers, score history, prioritization inputs, and residual-risk calculations
- `ai-orchestration-service`: Non-authoritative AI proposals and provenance
- `decision-work-service`: Recommendations, decisions, work orders/actions, completion reports, and verification
- `reporting-service`: Read models and portfolio projections across the authoritative services
- `geospatial-service`: Spatial projections and map-oriented queries, not a second asset registry

### Spatial and live hazard data

Asset coordinates are authoritative location data owned by the asset domain. The geospatial service keeps immutable location snapshots and hazard-layer snapshots; it does not create a second asset registry.

Live heat, flood, wind, fire, and vegetation data are ingested as versioned spatial observations. Polygon feeds are normalized to GeoJSON/WGS84 (`EPSG:4326`) for MapLibre. Each snapshot retains its provider, source URI, source observation time, ingestion time, validity interval, geometry, properties, and source event ID.

Spatial processing performs a point-in-polygon or nearest-feature join between an asset location snapshot and a hazard-layer snapshot. The result is an immutable exposure record linked to both source snapshots. Risk calculation consumes those exposure records as timestamped inputs. A new weather or hazard observation creates a new exposure and risk evaluation; it never overwrites prior source data or history.

MapLibre is a read projection over these records. The client can render asset points, risk/priority properties, and tenant-scoped hazard polygons or vector tiles, but it must call the owning service for any change.

Pole prioritization is a separate calculation from risk evaluation. It may combine risk score, hazard exposure, consequence, inspection confidence, criticality, age, and treatment urgency into a versioned `PolePriorityEvaluation`. A priority score helps sequence work; it does not authorize replacement or create a work assignment.

Cross-service records must use stable identifiers and tenant boundaries. Reporting and role-specific screens should consume projections/read models rather than duplicate authoritative asset records.

## Human personas and system actors

RiskLayer distinguishes between human personas and system actors. Personas are users who review, approve, route, execute, or verify work. System actors are software components that evaluate data, route risk, or generate non-authoritative recommendations.

### Human personas

- **Data Manager / Data Administrator**: authorizes data ingestion, source mapping, asset registry quality, and reference layer governance
- **Asset Manager / Planner**: owns asset program planning, lifecycle planning, and prioritization across the portfolio
- **Field Inspector**: performs inspections, creates findings, captures evidence, and can initiate new defect or observation records
- **Vegetation Management / Forestry**: owns vegetation risk pathways, treatment selection, contractor assignment, and verification of vegetation mitigation
- **Supervisor / QA-QC Reviewer**: reviews work quality, evidence, exceptions, and field compliance before a decision or verification is accepted
- **Risk & Resilience Analyst**: analyzes condition, exposure, consequence, and changing risk; explains the drivers; routes the risk to the proper owner; and monitors residual risk
- **Asset Engineer / Engineering**: evaluates structural alternatives, technical tolerances, replacement options, and engineering design review
- **Operations / Maintenance Manager**: manages operational response, maintenance execution, and field coordination
- **Finance / Program Manager**: prepares cost, budget, prioritization, and program-value analysis for higher-consequence decisions
- **Decision Maker / Executive**: approves, rejects, modifies, or defers recommendations according to configured policy and authority thresholds
- **Field Crew / Contractor**: performs the authorized work and submits completion evidence
- **Compliance / Regulatory**: reviews compliance exposure, obligations, and evidence requirements
- **System Administrator**: manages users, role mapping, approval rules, and technical configuration

### System actors

- **Risk Engine**: a system actor that evaluates asset condition, exposure, consequence, weather, wildfire hazard, vegetation growth, and other dynamic drivers to produce risk, confidence, risk drivers, and recommendations
- **AI Assist**: a non-authoritative recommendation engine that may suggest classifications, relationships, anomaly detection, routing options, or draft recommendations

Risk Engine output and AI output remain distinct. The Risk Engine is not a human persona and is never the final approving authority for work or risk decisions.

### Role-specific UX

Roles are views and permissions over the same underlying records:

- **Field Inspector:** assigned work, maps, assets, inspection forms, findings, photographs, GPS, and synchronization
- **Vegetation Management / Forestry:** vegetation queues, clearance issues, strike potential, wildfire-consequence areas, treatment status, contractors, verification, and trends
- **Risk & Resilience Analyst:** high-risk and changing assets, drivers, geographic concentrations, routing queues, residual risk, and overdue actions
- **Executive / Decision Maker:** portfolio risk, trends, critical exposures, decisions required, mitigation costs, expected risk reduction, deferred risk, and program performance
- **QA/QC Reviewer:** inspections awaiting review, exceptions, evidence, clarification requests, and work awaiting verification

These roles must not get separate copies of the domain model. They receive filtered, permission-aware projections of the same asset history.

### Vegetation-first data design

Vegetation must be treated as a first-class risk pathway rather than a field embedded only inside a pole inspection. Vegetation may be associated with one asset, multiple assets, a line segment, feeder, span, or a ROW area. The data model needs a relationship object that can connect vegetation conditions to multiple assets and to geospatial extents.

A vegetation condition can therefore be related through:

- a single asset record
- multiple asset records in a related set
- a span or feeder segment
- a defined ROW or vegetation area
- a geospatial polygon or hazard-affected extent

This prevents a vegetation issue from being trapped inside a single asset record when the same condition affects neighboring infrastructure or a corridor. Vegetation consequences should remain linked to the plant condition, risk drivers, location snapshots, treatment history, and resulting residual risk rather than being flattened into one pole record.

## Multi-device and offline operation

RiskLayer is responsive across desktop, laptop, tablet, and mobile devices. A user may move between devices during one workflow without creating a new asset, inspection, issue, or work record. Identity, authorization, and stable record identifiers remain consistent across devices.

Authorized field users can download an assignment package before entering an area without connectivity. The package may contain the required asset details, offline map data, relevant previous inspections, work instructions, and assigned activities. While offline, users may complete forms, create findings and issues, capture photographs and GPS, enter measurements and notes, and save incomplete work.

The client must visibly distinguish:

- Online
- Offline
- Synced
- Pending Sync
- Sync Failed

Offline writes are submitted through an idempotent synchronization queue using a client event identifier, device identifier, user identity, entity identity, operation, payload, attempt count, and error state. The server deduplicates client events so reconnecting does not create duplicate records. Conflicts require an explicit resolution policy; they must not be silently overwritten.

Field inspectors may create defects, vegetation issues, safety concerns, equipment issues, additional inspection requests, and other observations. A newly discovered asset is a `Provisional / Unverified Asset` until authorized review; it is not automatically added to the official asset registry.

## Contractor and external-user access

`Contractor / External Field User` is a restricted role. It may view authorized assignments, assigned assets, navigation data, work instructions, upload evidence, enter labor/material information where permitted, record completion, and submit work for verification.

It must not normally access the complete utility asset network, modify risk methodology or official risk scores, modify unrelated assets, approve its own work, manage users, or change system configuration. External access must be revocable, and access is constrained by tenant, contractor, project, territory, program, asset group, and operating district where configured.

Completion and verification remain separate events. Where practical, the performer cannot be the verifier. Verification creates the trigger for residual-risk evaluation; work is not considered complete merely because a completion report was submitted.

## Implementation rules

1. Do not add a recommendation field directly to a risk result as a substitute for a `Recommendation` record.
2. Do not use a boolean such as `approved` as the complete decision model; record the decision outcome, authority, rationale, timestamps, and any conditions.
3. Do not store findings only as strings on an inspection; findings need their own identity and lifecycle and must link back to their source condition/evidence.
4. Do not overwrite prior risk evaluations when re-scoring.
5. Do not let AI adapters persist authoritative asset, condition, finding, risk, recommendation, decision, work, completion, verification, or residual-risk records.
6. A workflow transition may create or request domain records, but it must not collapse the domain concepts into one generic state.
