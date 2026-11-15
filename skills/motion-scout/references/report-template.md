# Research report and Director handoff template

Use the useful fields below; populate real decisions/evidence rather than leaving
this template as the deliverable. Write user-facing reports in the user's language.

## Brief and run scope

Record mode, research timestamp, audience/style/visual jobs, aspect/resolution,
duration/fps, installed renderer/packages, local reusable pieces and restrictions.
List detected/tested tools and failures. Log current 7/30/90-day cutoffs, established
search lane, exact queries/sources, and any missing/empty scope.

## Candidate table

| Tier / confidence | Candidate / type | Visual + implementation evidence | License/security eligibility | Stack/adaptation | Momentum evidence |
| --- | --- | --- | --- | --- | --- |

For each finalist include canonical URL, inspected SHA/version, actual source paths,
manifest dependencies, license evidence, demo/docs/post links, visible/demonstrated
behavior and limits. Metadata includes dates, stars/forks/activity **when available**,
its source and observation timestamp. Unknown growth remains unknown.

Show criteria/evidence behind qualitative tiers or fully supported weighted scores.
Keep Verified Viral / Reported Viral / Exceptional / Experimental separate.
Distinguish observations, inference, proposed adaptations and unexecuted tests.

## Recommendation and handoff

Select the smallest set, explain why local alternatives are insufficient or better,
and describe the scene/effect each choice earns. Include acceptance tests, costs,
permissions and fallbacks. Research-only ends with this proposed plan.

Optional structured handoff (illustrative schema, not filled research):

```json
{
  "request_mode": "research-only",
  "creative_brief": {},
  "research_timestamp": null,
  "local_stack": {},
  "selected_technologies": [],
  "sources": [{
    "url": null,
    "inspected_sha_or_version": null,
    "implementation_paths": [],
    "required_dependencies": [],
    "license_and_notices": null,
    "security_eligibility": null,
    "compatibility_warnings": [],
    "adaptation_strategy": null,
    "visual_reference_urls": [],
    "visual_status": "unverified",
    "recent_growth": "unknown",
    "confidence": null,
    "tests_executed": []
  }],
  "recommended_shots_or_effect_jobs": [],
  "acceptance_tests": [],
  "remaining_limits": [],
  "next_action": null
}
```

## Validation and limits

Name what actually ran, which pages/code/demos were inspected, X access/metrics
limits and unverified assumptions. State whether studio/dependencies changed.
Link local/private evidence without copying it into public skill materials.
