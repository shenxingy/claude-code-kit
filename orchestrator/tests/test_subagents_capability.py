"""`subagents` was declared for both providers, read by nothing, and wrong twice.

First it was CONDITIONAL with no condition written anywhere, which reads as
"sometimes, depending" and explains nothing. Then, on 2026-09-02, it was
corrected to UNSUPPORTED on the premise that `codex exec` spawns no sub-agent.
That premise was false, and the way it was reached is the lesson: it was
reasoned from the absence of a delegation FLAG in `codex exec --help`, and a
missing flag is not a missing capability.

Measured 2026-09-05. This host's `~/.codex/state_5.sqlite` holds `source='exec'`
parent threads with depth-1 children using Clade's own agent roles, and a live
`codex exec --json` run reproduced one on CLI 0.153.4. In released upstream,
`collab_tools_enabled` (`codex-rs/core/src/tools/spec_plan.rs:647` at
`rust-v0.153.4`) branches only on the resolved model's `multi_agent_version`;
the session source is read once, to ask whether the caller is itself a
subagent, never to separate headless from interactive.

So the state is CONDITIONAL again — but this time the condition is written
down, which is the whole difference. These tests are the missing consumer:
they pin that the condition is stated, and that a run which MUST subdivide is
still refused on a route we cannot prove, because `resolve_capabilities`
admits only SUPPORTED for a REQUIRED capability.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from execution_envelope import (  # noqa: E402
    CapabilityRequirement,
    CapabilityState,
    RequirementLevel,
    RequiredCapabilityUnavailable,
    resolve_capabilities,
)
from worker_provider import ClaudeProvider, CodexProvider  # noqa: E402


def _caps(provider):
    return provider().capabilities()


def test_claude_can_subdivide_and_codex_depends_on_its_model() -> None:
    assert _caps(ClaudeProvider).state("subagents") is CapabilityState.SUPPORTED
    assert _caps(CodexProvider).state("subagents") is CapabilityState.CONDITIONAL


def test_codex_subagents_is_not_a_shrug() -> None:
    """CONDITIONAL earns its place only by naming what it depends on.

    The condition has to be the thing that actually decides it. Upstream gates
    the collaboration tools on the resolved model's catalog
    `multi_agent_version`, so that is what the source must name — not the
    adapter, and not a flag inventory, which is what produced the wrong answer
    last time.
    """
    caps = _caps(CodexProvider)
    assert caps.state("subagents") is CapabilityState.CONDITIONAL
    source = caps.sources["subagents"]
    assert "multi_agent_version" in source, source
    assert "AGENTS.md" in source, source
    assert "codex exec has no headless sub-agent spawn" not in source, (
        "the falsified premise must not come back as a reason"
    )


@pytest.mark.parametrize("provider", [ClaudeProvider, CodexProvider])
def test_every_conditional_capability_states_its_condition(provider) -> None:
    """A CONDITIONAL whose source is only the adapter name explains nothing."""
    caps = _caps(provider)
    adapter_only = {
        name
        for name, state in caps.states.items()
        if state is CapabilityState.CONDITIONAL and ":" not in caps.sources.get(name, "")
    }
    assert not adapter_only, f"conditional with no condition expressed: {sorted(adapter_only)}"


def _require_subagents(capabilities, level=RequirementLevel.REQUIRED):
    """The enforcement path a task reaches through execution_requirements."""
    return resolve_capabilities(
        capabilities,
        (CapabilityRequirement("subagents", level),),
    )


def test_a_fanout_task_is_refused_on_a_runtime_that_cannot_prove_it() -> None:
    """REQUIRED admits SUPPORTED only, so CONDITIONAL still refuses.

    This is why correcting the state did not weaken the gate: Codex can
    delegate, but whether THIS run's model will is not knowable here, and a
    task that must subdivide is not admitted on a maybe.
    """
    with pytest.raises(RequiredCapabilityUnavailable):
        _require_subagents(_caps(CodexProvider))


def test_a_fanout_task_is_admitted_on_a_runtime_that_can() -> None:
    _require_subagents(_caps(ClaudeProvider))  # must not raise


def test_a_preferred_fanout_degrades_rather_than_failing() -> None:
    """Preferred, not required: the run proceeds and the loss is recorded."""
    degradations = _require_subagents(_caps(CodexProvider), RequirementLevel.PREFERRED)
    assert [d.capability for d in degradations] == ["subagents"]
    assert degradations[0].resolved == "conditional"

    assert _require_subagents(_caps(ClaudeProvider), RequirementLevel.PREFERRED) == ()
