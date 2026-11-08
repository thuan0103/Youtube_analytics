# Social Trend Intelligence

## 1. Project Overview

### 1.1 Purpose

Social Trend Intelligence is an AI-assisted research system for
discovering and analyzing trending topics across YouTube and TikTok.

The user interacts with the system using natural language. The system
interprets the request, plans the research workflow, collects available
platform data, analyzes trends, generates evidence-backed insights, and
produces an interactive HTML report (an artifact) that the user can open
in a browser.

The product should feel like a lightweight research assistant rather
than a conventional analytics dashboard.

### 1.2 Core user experience

A user might ask:

> Analyze AI Agent trends in Vietnam over the last 7 days on YouTube and
> TikTok. Identify fast-growing topics, compare the platforms, and
> create an interactive report.

Expected system behavior:

1.  Understand the research question.
2.  Extract topic, region, platforms, date range, and requested
    analysis.
3.  Validate whether the request is sufficiently clear and supported.
4.  Create a bounded research plan.
5.  Collect data from supported sources.
6.  Normalize and persist the collected data.
7.  Calculate metrics and discover topic clusters.
8.  Generate evidence-backed insights.
9.  Render an interactive HTML report.
10. Show the report in Gradio and make it available to open/download.

### 1.3 Product principles

-   Natural-language-first interaction.
-   Evidence-backed analysis: every important claim should be traceable
    to data.
-   Deterministic calculations: Python computes metrics; LLMs explain
    them.
-   Explicit source and data-coverage limitations.
-   Modular architecture with clear interfaces.
-   No unnecessary agents or infrastructure.
-   HTML reports are rendered from validated structured data, not
    arbitrary LLM-generated code.

------------------------------------------------------------------------

## 2. Goals and Non-goals

### 2.1 MVP goals

-   [ ] Accept a natural-language research question in Gradio.
-   [ ] Extract a structured research request.
-   [ ] Generate and validate a research plan.
-   [ ] Collect YouTube data through an authorized API.
-   [ ] Ingest TikTok data through an approved API, licensed provider,
    or user-supplied CSV/JSON dataset.
-   [ ] Normalize records into a common video schema.
-   [ ] Calculate baseline trend metrics.
-   [ ] Discover related topics using text embeddings and clustering.
-   [ ] Generate trend analysis and cross-platform comparisons.
-   [ ] Create an interactive HTML report.
-   [ ] Display workflow progress and report status in Gradio.
-   [ ] Store research runs, source records, metrics, and report
    metadata.

### 2.2 Non-goals for the MVP

-   Training a custom foundation model.
-   Automatically downloading or analyzing every video.
-   Unapproved scraping or bypassing platform restrictions.
-   Real-time streaming analytics.
-   Predicting future virality with claims of certainty.
-   Multi-user enterprise permissions and billing.
-   Microservices, Kubernetes, Kafka, or distributed task
    infrastructure.
-   Letting an LLM generate and execute arbitrary Python, HTML, or
    JavaScript.

### 2.3 Important data limitation

The availability and fields of social-platform data depend on API
permissions, quotas, region, and provider terms. TikTok access is
especially restricted for many developer use cases. The MVP must not
assume unrestricted public search access.

The system should use a provider abstraction and support imported
datasets so the analytics and agent workflow can be developed before
every data source is available.

------------------------------------------------------------------------

## 3. Scope and Functional Requirements

  -----------------------------------------------------------------------
  ID                      Requirement             Priority
  ----------------------- ----------------------- -----------------------
  FR-01                   User can submit a       Must
                          natural-language        
                          research question       

  FR-02                   System extracts topic,  Must
                          region, platforms, and  
                          time range              

  FR-03                   System asks for         Should
                          clarification when      
                          essential information   
                          is missing              

  FR-04                   System creates a        Must
                          structured research     
                          plan                    

  FR-05                   System collects data    Must
                          from supported platform 
                          adapters                

  FR-06                   System supports         Must
                          CSV/JSON import for     
                          unavailable platform    
                          access                  

  FR-07                   System normalizes and   Must
                          deduplicates video      
                          records                 

  FR-08                   System calculates       Must
                          baseline trend metrics  

  FR-09                   System clusters         Should
                          semantically related    
                          video topics            

  FR-10                   System generates        Must
                          evidence-backed         
                          insights                

  FR-11                   System compares         Should
                          platforms when          
                          comparable data exists  

  FR-12                   System generates an     Must
                          interactive HTML report 

  FR-13                   User can open or        Must
                          download the report     

  FR-14                   System stores research  Should
                          history and report      
                          metadata                

  FR-15                   System logs tool        Should
                          execution, errors,      
                          duration, and token     
                          usage                   

  FR-16                   User can ask follow-up  Later
                          questions about a       
                          completed research run  
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 4. Proposed System Architecture

### 4.1 Architecture style

Use a **modular monolith** for the MVP. All modules run within one
Python application. Modules communicate through Python interfaces and
Pydantic data contracts.

Gradio is the user interface and application entry point. CrewAI Flows
orchestrate the research process. There is no separate Flask or FastAPI
server in the MVP.

### 4.2 Logical architecture

``` text
+------------------------------------------------------+
|                     Gradio UI                        |
| Natural-language input | Progress | Report access    |
+------------------------------+-----------------------+
                               |
                               v
+------------------------------------------------------+
|                 Application / Use Cases              |
| SubmitResearch | GetResearchStatus | GetReport        |
+------------------------------+-----------------------+
                               |
                               v
+------------------------------------------------------+
|                    CrewAI Flow                       |
| Request understanding -> Planning -> Execution       |
| -> Analysis -> Insight -> Report -> Validation       |
+------------------------------+-----------------------+
                               |
             +-----------------+------------------+
             |                 |                  |
             v                 v                  v
      Platform Tools     Analytics Engine    Agent Crews
      YouTube adapter    Metrics             Trend analyst
      TikTok adapter     Clustering          Comparison analyst
      Dataset importer   Topic ranking       Insight/report agent
             |                 |                  |
             +-----------------+------------------+
                               |
                               v
+------------------------------------------------------+
|                    Persistence                       |
| PostgreSQL | Optional pgvector | HTML artifact files |
+------------------------------------------------------+
```

### 4.3 Component responsibilities

  Component                Responsibility                                 Uses an LLM?
  ------------------------ ---------------------------------------------- --------------
  Gradio UI                Collect input and display progress/results     No
  Intent Analyzer          Interpret natural-language request             Yes
  Research Planner         Create a bounded execution plan                Yes
  Platform adapters        Fetch/import platform data                     No
  Normalizer               Validate and standardize records               No
  Analytics engine         Calculate metrics and clusters                 Usually no
  Trend Analyst            Explain analytical results                     Yes
  Cross-platform Analyst   Interpret platform differences                 Yes
  Insight Analyst          Identify opportunities and caveats             Yes
  Report Agent             Produce structured narrative sections          Yes
  HTML renderer            Render report templates and charts             No
  Report validator         Check required fields and artifact integrity   No

**Design rule:** Do not create an agent for deterministic
data-processing tasks. Agents should be used where language
understanding, synthesis, or bounded reasoning is valuable.

------------------------------------------------------------------------

## 5. End-to-End Workflow

### 5.1 Main workflow

``` text
START
  |
  v
Receive user question
  |
  v
Intent Analyzer
  |
  v
Validate ResearchRequest
  |
  +---- Missing essential information? ---- Yes ---> Ask user
  |                                             |
  No <------------------------------------------+
  |
  v
Research Planner
  |
  v
Validate ResearchPlan and allowed operations
  |
  v
Collect data from selected sources
  |                         |
  v                         v
YouTube adapter         TikTok adapter / dataset
  |                         |
  +------------+------------+
               |
               v
        Normalize records
               |
               v
       Deduplicate and persist
               |
               v
       Calculate analytics
               |
               v
       Discover topic clusters
               |
               v
       Trend analysis agents
               |
               v
       Validate evidence and claims
               |
               v
       Build structured report data
               |
               v
       Render HTML artifact
               |
               v
       Validate artifact
               |
               v
       Return report to Gradio
               |
              END
```

### 5.2 Workflow rules

-   Collectors may run concurrently when the selected sources are
    independent.
-   Analytics runs only after collection and normalization have
    completed.
-   Cross-platform comparison runs only when there is usable data from
    at least two platforms.
-   If one platform fails, the workflow may continue with the available
    platform and clearly mark the report as partial.
-   The planner may select only predefined tools and operations.
-   A failed step should produce a typed error and a bounded retry
    policy.
-   The flow must not claim that a platform was analyzed if no valid
    data was collected from it.

### 5.3 Suggested CrewAI Flow stages

1.  `understand_request`
2.  `validate_request`
3.  `create_research_plan`
4.  `collect_platform_data`
5.  `normalize_data`
6.  `run_analytics`
7.  `run_topic_analysis`
8.  `generate_insights`
9.  `build_report_data`
10. `render_artifact`
11. `validate_artifact`
12. `complete_research`

Use Flow state for orchestration and pass validated Pydantic objects
between components. Avoid placing large raw datasets directly into LLM
prompts or Flow state when database references are sufficient.

------------------------------------------------------------------------

## 6. Agent Design

### 6.1 Intent Analyzer Agent

**Purpose:** Convert a natural-language question into a structured
`ResearchRequest`.

Responsibilities: - Identify the user's research objective. - Extract
topic or keywords. - Identify target platforms. - Extract region and
time range. - Identify requested analysis types. - Identify missing or
ambiguous constraints.

Must not: - Collect data. - Invent unsupported platform capabilities. -
Make claims about trend results before data collection.

### 6.2 Research Planner Agent

**Purpose:** Create an execution plan from a validated request.

Responsibilities: - Select supported collection sources. - Choose
allowed analysis operations. - Define execution order and
dependencies. - Set reasonable collection limits. - Identify expected
outputs.

Safety and reliability: - Planner outputs are structured and
validated. - The plan references an allowlist of operation IDs. - The
plan cannot contain arbitrary executable code. - Enforce maximum
collection limits, timeouts, and retry limits in Python.

### 6.3 Trend Analyst Agent

**Purpose:** Explain the output of the analytics engine.

Responsibilities: - Explain the strongest topic clusters. - Describe
evidence for increasing or decreasing activity. - Identify notable
keywords and content patterns. - Distinguish observed facts from
interpretations.

### 6.4 Cross-platform Analyst Agent

**Purpose:** Compare trends across YouTube and TikTok.

Responsibilities: - Identify topics present on both platforms. -
Identify platform-specific topics. - Explain differences in content
format and engagement where data supports it. - Note data coverage and
metric comparability limitations.

Do not directly compare raw views or engagement rates as if platform
definitions and sampling were identical. Normalize carefully and
disclose limitations.

### 6.5 Insight Analyst Agent

**Purpose:** Generate useful research implications.

Responsibilities: - Identify potential content opportunities. - Identify
emerging themes and unanswered questions. - Explain why a topic may
deserve further investigation. - Provide confidence and supporting
evidence.

Avoid presenting speculation as fact or guaranteeing future growth.

### 6.6 Report Agent

**Purpose:** Produce structured report sections.

Responsibilities: - Create an executive summary. - Summarize key
findings. - Explain metrics and topic clusters. - Include limitations
and methodology. - Attach references to supporting record IDs.

The Report Agent outputs structured data, not executable HTML or
JavaScript.

### 6.7 Agent count for MVP

Start with: - Intent Analyzer - Research Planner - Trend Analyst -
Cross-platform Analyst - Report/Insight Agent

Some responsibilities can share one Crew initially. Split into separate
Crews only when there is a clear need for different context, tools, or
evaluation.

------------------------------------------------------------------------

## 7. Data Collection Design

### 7.1 Provider abstraction

Define a common interface for data providers.

``` python
from abc import ABC, abstractmethod

class PlatformCollector(ABC):
    @abstractmethod
    def search_videos(self, request):
        raise NotImplementedError
```

### 7.2 YouTube

Potential source: YouTube Data API v3.

Possible operations: - Search videos by query. - Retrieve video
metadata. - Retrieve available statistics. - Retrieve channel metadata
where permitted and useful.

Important: - Respect API quotas and terms. - Search results and
statistics have different API operations. - A current view count is not
historical growth. - To calculate velocity or growth, collect repeated
snapshots over time.

### 7.3 TikTok

The implementation must depend on an authorized and permitted data
source.

MVP fallback: - Import a documented CSV/JSON dataset. - Keep
provider-specific ingestion separate from analytics. - Record dataset
provenance, collection time, and field definitions.

Do not make the project dependent on unapproved scraping or
access-control circumvention.

### 7.4 Collection metadata

Every collection run should record: - Provider/source. - Query and
filters. - Requested time range. - Collection timestamp. - Number of
records returned. - Number of valid records. - Pagination status. -
Errors and quota information where available. - Data coverage notes.

------------------------------------------------------------------------

## 8. Data Model and Pydantic Contracts

These are initial contracts and should be refined before implementation.

### 8.1 ResearchRequest

``` python
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

Platform = Literal["youtube", "tiktok"]

class ResearchRequest(BaseModel):
    question: str
    topic: str
    keywords: list[str] = Field(default_factory=list)
    region: str | None = None
    platforms: list[Platform]
    start_date: datetime | None = None
    end_date: datetime | None = None
    relative_days: int | None = None
    analysis_types: list[str] = Field(default_factory=list)
    output_format: Literal["html"] = "html"
```

### 8.2 ResearchPlan

``` python
from pydantic import BaseModel, Field

class ResearchStep(BaseModel):
    step_id: str
    operation: str
    description: str
    depends_on: list[str] = Field(default_factory=list)
    parameters: dict = Field(default_factory=dict)

class ResearchPlan(BaseModel):
    objective: str
    steps: list[ResearchStep]
    expected_outputs: list[str]
    collection_limit_per_platform: int
```

Validate every `operation` against an allowlist in application code.

### 8.3 VideoMetadata

``` python
from datetime import datetime
from pydantic import BaseModel, Field

class VideoMetadata(BaseModel):
    platform: str
    video_id: str
    title: str
    description: str | None = None
    author_id: str | None = None
    author_name: str | None = None
    published_at: datetime | None = None
    collected_at: datetime
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    hashtags: list[str] = Field(default_factory=list)
    video_url: str | None = None
    source_id: str
```

### 8.4 AnalyticsResult

Suggested fields: - `research_run_id` - `total_videos` -
`platform_coverage` - `metric_definitions` - `topic_clusters` -
`video_rankings` - `time_series` - `data_quality_warnings`

### 8.5 TrendInsight

Suggested fields: - `title` - `summary` - `topic_ids` -
`evidence_record_ids` - `observation` - `interpretation` -
`confidence` - `limitations`

### 8.6 ReportArtifact

``` python
from datetime import datetime
from pydantic import BaseModel

class ReportArtifact(BaseModel):
    report_id: str
    research_run_id: str
    title: str
    file_path: str
    created_at: datetime
    status: str
    source_count: int
    topic_count: int
```

The artifact path must be generated by the application, not accepted
directly from an LLM response.

------------------------------------------------------------------------

## 9. Analytics Engine

### 9.1 Baseline metrics

  -----------------------------------------------------------------------
  Metric                  Meaning                 Requirements
  ----------------------- ----------------------- -----------------------
  View count              Observed views          Source provides views

  Engagement count        Likes + comments, and   Field definitions must
                          shares if available     be known

  Engagement rate         Engagement divided by   Guard against
                          views                   missing/zero views

  View velocity           Change in views per     Requires at least two
                          unit of time            snapshots

  Growth rate             Relative change over a  Requires comparable
                          period                  snapshots

  Topic popularity        Number or share of      Depends on collection
                          collected records in a  coverage
                          topic                   

  Trend score             Combined normalized     Document weights and
                          indicators              limitations
  -----------------------------------------------------------------------

Example:

``` python
def engagement_rate(likes: int, comments: int, views: int) -> float | None:
    if views <= 0:
        return None
    return (likes + comments) / views
```

This is a baseline formula only. If share counts are unavailable, do not
imply that they are included.

### 9.2 Trend score

A possible initial score:

`trend_score = 0.35 * velocity + 0.25 * engagement + 0.25 * growth + 0.15 * popularity`

All components must be normalized to a comparable range before
combining.

The weights are hypotheses for an initial experiment, not universal
truths. Store the score version and component values so results are
explainable.

### 9.3 Topic discovery

Possible pipeline: 1. Prepare title, description, and hashtag text. 2.
Clean and normalize text. 3. Generate embeddings with a suitable
multilingual model. 4. Cluster embeddings using HDBSCAN or another
tested method. 5. Extract representative keywords. 6. Use an LLM to
generate readable topic labels from representative examples. 7. Store
cluster membership and representative record IDs.

Do not assume every record belongs to a meaningful cluster. Support an
unassigned/noise category.

### 9.4 Trend interpretation

A single collection snapshot can show popularity within the collected
sample, but cannot prove growth over time. Growth claims require
repeated snapshots or a reliable historical dataset.

------------------------------------------------------------------------

## 10. Artifact Generation Engine

### 10.1 Design principle

Use a deterministic rendering pipeline:

``` text
AnalyticsResult + TrendInsight
              |
              v
       Report Agent
              |
              v
       ReportData (Pydantic)
              |
              v
       Jinja2 HTML Template
              |
              +---- Plotly charts
              |
              v
       HTML Validation
              |
              v
       Stored HTML Artifact
```

### 10.2 Report sections

1.  Cover / research question.
2.  Executive summary.
3.  Research scope and methodology.
4.  Data coverage and collection status.
5.  Key metrics.
6.  Trending topic cards.
7.  Trend charts and time series.
8.  YouTube vs TikTok comparison.
9.  Top videos and source links.
10. AI-generated insights.
11. Limitations and confidence notes.
12. Sources and collection timestamps.

### 10.3 HTML rendering

Recommended technologies: - Jinja2 for templates. - Plotly for
interactive charts. - CSS for responsive design. - Optional small,
trusted JavaScript components.

The renderer should: - Escape untrusted text. - Validate URLs before
making them clickable. - Avoid arbitrary script injection. - Use known
templates and chart configurations. - Generate unique report IDs and
safe filenames. - Keep report data separate from presentation.

### 10.4 Artifact storage

MVP options: - Save reports under `artifacts/reports/`. - Store report
metadata in PostgreSQL. - Return the generated file through Gradio's
file component. - Provide a browser preview where supported by the
Gradio version.

------------------------------------------------------------------------

## 11. RAG and Follow-up Questions

RAG is a later milestone, not a prerequisite for the first working
version.

### 11.1 Use cases

-   Ask why a topic was ranked highly.
-   Retrieve videos supporting an insight.
-   Ask for a summary of a topic cluster.
-   Compare a current research run with a previous run.
-   Ask follow-up questions about a generated report.

### 11.2 Retrieval strategy

Use hybrid retrieval: - PostgreSQL for exact filters and numeric
queries. - pgvector for semantic retrieval over titles, descriptions,
and insight text. - Metadata filters for platform, date, topic, and
research run.

Do not use vector search for exact totals, rankings, or metric
calculations.

------------------------------------------------------------------------

## 12. Database Design

Suggested initial tables:

  Table                       Purpose
  --------------------------- -------------------------------------
  `research_runs`             User request, status, timestamps
  `research_plans`            Validated plan for each run
  `data_sources`              Provider and dataset provenance
  `videos`                    Normalized video metadata
  `video_snapshots`           Time-series statistics
  `topic_clusters`            Discovered topic groups
  `video_topic_memberships`   Video-to-topic mapping
  `analytics_results`         Computed metrics and rankings
  `trend_insights`            Structured AI insights
  `reports`                   Artifact metadata and file location
  `agent_executions`          Agent/flow execution logs

Use stable unique constraints such as `(platform, video_id)` for video
identity. Keep snapshots separate from the current video record so
historical metrics can be analyzed.

pgvector can be added when semantic retrieval is implemented. It is not
required for the initial collector and analytics milestone.

------------------------------------------------------------------------

## 13. Proposed Project Structure

``` text
social-trend-intelligence/
│
├── app/
│   ├── main.py
│   ├── ui/
│   │   ├── gradio_app.py
│   │   ├── chat_view.py
│   │   ├── progress_view.py
│   │   └── report_view.py
│   ├── agents/
│   │   ├── intent_analyzer.py
│   │   ├── research_planner.py
│   │   ├── trend_analyst.py
│   │   ├── cross_platform_analyst.py
│   │   └── report_agent.py
│   ├── flows/
│   │   ├── trend_flow.py
│   │   ├── state.py
│   │   └── events.py
│   ├── tools/
│   │   ├── youtube/
│   │   │   ├── collector.py
│   │   │   └── client.py
│   │   ├── tiktok/
│   │   │   ├── collector.py
│   │   │   └── importer.py
│   │   └── analytics/
│   │       ├── metrics.py
│   │       ├── clustering.py
│   │       └── scoring.py
│   ├── services/
│   │   ├── research_service.py
│   │   ├── collection_service.py
│   │   ├── analytics_service.py
│   │   └── artifact_service.py
│   ├── schemas/
│   │   ├── research.py
│   │   ├── video.py
│   │   ├── analytics.py
│   │   ├── insight.py
│   │   └── report.py
│   ├── repositories/
│   │   ├── video_repository.py
│   │   ├── research_repository.py
│   │   └── report_repository.py
│   ├── integrations/
│   │   ├── llm.py
│   │   ├── embeddings.py
│   │   └── database.py
│   └── artifacts/
│       ├── renderer.py
│       ├── validator.py
│       └── templates/
│           ├── base.html
│           └── trend_report.html
├── data/
│   ├── imports/
│   └── samples/
├── artifacts/
│   └── reports/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── evaluation/
├── docs/
│   ├── architecture.md
│   └── decisions/
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements.txt
```

This is a proposed structure, not a requirement to create every file
immediately. Add modules when their milestone begins.

------------------------------------------------------------------------

## 14. Design Patterns to Apply

  -----------------------------------------------------------------------
  Pattern                 Where                   Why
  ----------------------- ----------------------- -----------------------
  Adapter                 Platform collectors     Hide provider-specific
                                                  APIs

  Strategy                Metric/scoring          Swap analysis
                          algorithms              strategies

  Repository              Persistence             Separate data access
                                                  from business logic

  Factory                 Collector and LLM       Centralize object
                          construction            creation

  Dependency Injection    Services and agents     Make components
                                                  testable

  Orchestrator            CrewAI Flow             Coordinate workflow

  Pipeline                Data processing         Make processing stages
                                                  explicit

  Template Method /       HTML reports            Separate report layout
  Template Engine                                 from data

  Retry with Backoff      External API tools      Handle transient
                                                  failures

  Circuit Breaker (later) External providers      Avoid repeated failing
                                                  calls
  -----------------------------------------------------------------------

Do not apply patterns merely to increase the number of abstractions. Use
them when they solve a real maintenance or testing problem.

------------------------------------------------------------------------

## 15. Error Handling and Reliability

Expected failure cases: - Invalid or ambiguous user request. -
Unsupported platform or unavailable provider. - API quota exceeded. -
Network timeout. - Empty search results. - Incomplete metadata. -
Duplicate records. - LLM output fails schema validation. - Agent
execution fails. - HTML rendering or validation fails.

Rules: - Use typed exceptions at module boundaries. - Retry only
transient failures. - Use bounded retries and timeouts. - Preserve
partial collection results. - Mark reports as partial when
appropriate. - Never fabricate missing metrics or sources. - Include
collection and analysis timestamps in reports. - Log errors without
exposing API keys or secrets.

------------------------------------------------------------------------

## 16. Evaluation and Testing Strategy

### 16.1 Unit tests

-   Metric calculations.
-   Normalization.
-   Deduplication.
-   Date-range handling.
-   Trend scoring.
-   Schema validation.
-   HTML escaping and URL validation.

### 16.2 Integration tests

-   YouTube adapter with mocked API responses.
-   TikTok importer with sample datasets.
-   Database repositories.
-   CrewAI Flow with mocked tools/LLM.
-   HTML report generation.

### 16.3 Agent evaluation

Evaluate: - Intent extraction accuracy. - Correct platform and date
interpretation. - Plan validity. - Tool selection correctness. -
Evidence support for insights. - Structured output validity. - Report
completeness.

### 16.4 Report quality checks

Every generated report should: - State the research question and
scope. - Show collection timestamps and source coverage. - Distinguish
measured metrics from AI interpretation. - Link claims to supporting
records where possible. - Disclose missing data and comparison
limitations. - Avoid unsupported claims of growth or virality.

------------------------------------------------------------------------

## 17. Security and Configuration

-   Store credentials in environment variables.
-   Commit `.env.example`, never `.env`.
-   Validate user input and imported files.
-   Limit file size and accepted formats.
-   Sanitize text rendered into HTML.
-   Validate external URLs.
-   Do not execute LLM-generated code.
-   Restrict report output paths to the configured artifact directory.
-   Keep provider terms and data provenance with collected records.

------------------------------------------------------------------------

## 18. Implementation Roadmap

### Milestone 0 --- Project Foundation

-   [ ] Create repository and Python environment.
-   [ ] Configure formatting, linting, and tests.
-   [ ] Create `.env.example`.
-   [ ] Define initial Pydantic contracts.
-   [ ] Set up PostgreSQL connection.
-   [ ] Create architecture decision records.

**Exit criteria:** Application starts, schemas validate, database
connection works.

### Milestone 1 --- Data Foundation

-   [ ] Implement YouTube collector.
-   [ ] Implement TikTok CSV/JSON importer.
-   [ ] Define common collector interface.
-   [ ] Normalize video metadata.
-   [ ] Deduplicate records.
-   [ ] Persist video records.
-   [ ] Persist periodic statistics snapshots.

**Exit criteria:** A research query or imported dataset produces
normalized, stored records with provenance.

### Milestone 2 --- Analytics Engine

-   [ ] Implement engagement metrics.
-   [ ] Implement snapshot-based velocity and growth.
-   [ ] Implement topic text preparation.
-   [ ] Generate embeddings.
-   [ ] Implement clustering.
-   [ ] Implement trend scoring.
-   [ ] Add analytics tests.

**Exit criteria:** Given a known dataset, the system produces
reproducible metrics and topic clusters.

### Milestone 3 --- CrewAI Agents and Flow

-   [ ] Implement Intent Analyzer.
-   [ ] Implement Research Planner.
-   [ ] Implement Flow state.
-   [ ] Implement collection tools.
-   [ ] Implement analysis agents.
-   [ ] Add conditional workflow paths.
-   [ ] Add retries and partial-result handling.
-   [ ] Validate all agent outputs.

**Exit criteria:** A natural-language request runs through the workflow
and returns a validated analysis result.

### Milestone 4 --- HTML Artifact Engine

-   [ ] Define `ReportData` schema.
-   [ ] Implement Report Agent.
-   [ ] Build Jinja2 base template.
-   [ ] Build report sections.
-   [ ] Add Plotly charts.
-   [ ] Implement safe artifact naming and storage.
-   [ ] Validate generated HTML.
-   [ ] Add report tests.

**Exit criteria:** A completed research run produces a valid,
interactive HTML report with traceable sources.

### Milestone 5 --- Gradio Application

-   [ ] Build chat/input interface.
-   [ ] Connect submission to research use case.
-   [ ] Display workflow status.
-   [ ] Display partial/failure status.
-   [ ] Show report preview or open/download link.
-   [ ] Show research history.

**Exit criteria:** A user can submit a question and access the resulting
report from Gradio.

### Milestone 6 --- RAG and Evaluation

-   [ ] Add pgvector.
-   [ ] Index report and video text.
-   [ ] Implement semantic retrieval.
-   [ ] Implement follow-up Q&A.
-   [ ] Add agent tracing.
-   [ ] Build evaluation dataset.
-   [ ] Measure quality, latency, and token usage.

**Exit criteria:** Users can ask evidence-grounded follow-up questions
and the system has repeatable evaluation tests.

------------------------------------------------------------------------

## 19. MVP Definition of Done

The MVP is complete when:

-   [ ] User can submit a natural-language trend research request.
-   [ ] The system extracts and validates the request.
-   [ ] The system can collect YouTube data.
-   [ ] The system can ingest TikTok data from a permitted source or
    dataset.
-   [ ] Records are normalized and persisted.
-   [ ] Metrics and topic analysis are reproducible.
-   [ ] CrewAI Flow orchestrates the process.
-   [ ] Agents produce structured, evidence-backed explanations.
-   [ ] The system creates an interactive HTML artifact.
-   [ ] The user can open or download the report in Gradio.
-   [ ] Failures and partial data are clearly disclosed.
-   [ ] Core modules have unit and integration tests.

------------------------------------------------------------------------

## 20. Open Decisions --- To Be Confirmed

These decisions should remain open until explicitly agreed.

  -----------------------------------------------------------------------
  Decision                Current proposal        Status
  ----------------------- ----------------------- -----------------------
  Initial market          Vietnam                 To confirm

  Initial topics          Any topic, with         To confirm
                          keyword-based research  

  Initial platform access YouTube API + TikTok    Proposed
                          dataset import          

  LLM provider            GPT or Gemini           To decide

  Embedding model         Multilingual Sentence   To decide
                          Transformers            

  Database                PostgreSQL              Proposed

  Vector search           pgvector in a later     Proposed
                          milestone               

  Report style            Interactive research    To design
                          report                  

  Collection schedule     On-demand first;        Proposed
                          scheduled collection    
                          later                   

  Deployment              Local development first Proposed
  -----------------------------------------------------------------------

### Questions for the next design review

1.  Should the first version focus on Vietnam, global trends, or both?
2.  Should users be able to research any topic, or only predefined
    categories?
3.  Which LLM provider should be used?
4.  Should the first report prioritize a polished editorial layout or a
    data-dense analytics layout?
5.  Should research history and report comparison be part of the MVP or
    a later milestone?

------------------------------------------------------------------------

## 21. Recommended First Implementation Tasks

Do these tasks in order:

1.  Confirm the open decisions in Section 20.
2.  Create the repository and Python environment.
3.  Finalize `ResearchRequest`, `ResearchPlan`, `VideoMetadata`,
    `AnalyticsResult`, and `ReportArtifact`.
4.  Define collector interfaces.
5.  Implement the YouTube collector and TikTok dataset importer.
6.  Build a small, documented sample dataset for repeatable tests.
7.  Implement baseline analytics before introducing agents.
8.  Add CrewAI Flow and agents after the tools are testable.
9.  Build the HTML artifact renderer.
10. Connect the workflow to Gradio.

**Architecture principle to preserve:** Agents reason and coordinate;
Python tools collect and calculate; CrewAI Flow orchestrates; Pydantic
defines contracts; the artifact engine renders the final report.

------------------------------------------------------------------------

## Change Log

  Version   Date         Changes
  --------- ------------ -------------------------------------
  0.1       2026-11-08   Initial project scope and TDD draft
