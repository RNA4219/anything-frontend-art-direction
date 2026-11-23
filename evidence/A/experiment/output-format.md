# Common output serialization (both arms)

Write a JSON object with the following fields. This describes data shape, not preferred design decisions. Use the input brief's case, role, goal, requirement and feature IDs. Additional feature IDs may begin `add_`.

```json
{
  "schema_version": "1.0",
  "case_id": "the input case_id",
  "visual_intent_id": "the input visual_intent.id",
  "features": [{
    "id": "feature ID", "label": "human label",
    "disposition": "keep|merge|defer|remove", "target": null,
    "object": "the domain object", "outcome": "the capability",
    "roles": ["role ID"], "goal_ids": ["goal ID"],
    "requirement_ids": ["requirement ID"], "dependencies": ["feature ID"],
    "reason": "reason for the design decision",
    "priority": "required|high|medium|low", "priority_basis": "reason for priority"
  }],
  "screens": [{
    "id": "screen ID", "title": "screen label", "purpose": "screen purpose",
    "goal_ids": ["goal ID"], "feature_ids": ["feature ID"],
    "roles": ["role ID"], "entry_for": ["role for which this is an entry"],
    "information": [{"id": "information ID", "visibility": "primary|secondary", "reason": "reason"}]
  }],
  "navigation": [{
    "from": "screen ID", "to": "screen ID", "label": "visible label",
    "roles": ["role ID"], "kind": "global|local|contextual", "rationale": "reason"
  }],
  "goal_routes": [{"goal_id": "goal ID", "start_screen": "screen ID", "target_screen": "screen ID", "notes": "explanation"}],
  "unresolved": [{
    "id": "issue ID", "category": "function|information_architecture|interaction|visual|implementation",
    "owner": "A|B|C|D|product", "impact": "consequence", "blocking": false, "question": "what remains unknown"
  }],
  "decision_notes": ["notes on assumptions and decisions"]
}
```

Values separated by `|` are alternatives, not literal values. `target` is a feature ID for a merge and null otherwise. `primary` means information available on the screen without a disclosure action; scrolling is allowed. `secondary` is information behind disclosure or a supplemental area. Empty arrays are allowed. Use the supplied information IDs when referring to content. Write concrete plans for the briefs, not the illustrative values above.
