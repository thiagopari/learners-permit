// Learner's Permit: who may command what. Cedar is default-deny, and forbid beats permit.
// The /run choke point fills `context` from the session, clock, sensors and licence store.
// Nothing in it comes from LLM text.

// The AI agent works only inside its envelope, and only with skills that earned a licence.
permit (principal in Role::"ai_agent", action in [Action::"pick_place", Action::"move_to"], resource in Zone::"cell1")
when { ["banana","dish","housing","lid"].contains(context.object_class) && ["A","B","bin"].contains(context.bin)
       && context.speed_pct <= 50 && context.hour >= 6 && context.hour < 22
       && context.skill_licensed };

// A supervisor can approve one specific command outside the envelope (single-use token).
permit (principal in Role::"ai_agent", action == Action::"pick_place", resource in Zone::"cell1")
when { context has approver && context.approver in Role::"supervisor" && context.speed_pct <= 50 };

permit (principal in Role::"operator", action in [Action::"pick_place", Action::"move_to"], resource in Zone::"cell1")
when { context.speed_pct <= 80 };

permit (principal in Role::"supervisor", action in [Action::"change_mode", Action::"set_speed_limit"], resource in Zone::"cell1");

permit (principal in Role::"maintenance", action == Action::"change_mode", resource in Zone::"maint")
when { context.speed_pct <= 25 };

// The AI never changes modes or limits, even with an approval.
forbid (principal in Role::"ai_agent", action in [Action::"change_mode", Action::"set_speed_limit"], resource);

// Fail closed when the PEP forgets a field; slow down when a person is in the cell.
forbid (principal, action, resource) unless { context has human_in_zone && context has speed_pct
       && (!context.human_in_zone || context.speed_pct <= 25) };
