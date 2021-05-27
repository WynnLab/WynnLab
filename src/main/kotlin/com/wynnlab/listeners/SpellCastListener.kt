package com.wynnlab.listeners

import com.wynnlab.WynnClass
import com.wynnlab.api.*
import com.wynnlab.classes
import com.wynnlab.classes.BaseClass
import com.wynnlab.classes.BasePlayerSpell
import com.wynnlab.events.SpellCastEvent
import com.wynnlab.spells.Spell
import com.wynnlab.util.RefreshRunnable
import org.bukkit.Sound
import org.bukkit.entity.Player
import org.bukkit.event.EventHandler
import org.bukkit.event.EventPriority
import kotlin.math.ceil
import kotlin.math.floor

class CastListener : BaseListener() {
    @EventHandler(priority = EventPriority.HIGH)
    fun onSpellCast(e: SpellCastEvent) {
        val player = e.player
        val spellClass = player.getWynnClass()?.let { classes[it] } ?: return
        val spellId = e.spellId
        val spell = ((spellClass as? WynnClass)?.spells ?: (spellClass as BaseClass).spells)[spellId]

        val cost = cost(player, spellId, (spell as? Spell)?.cost ?: 0)

        if (spellId > 0) {
            player.data.setInt("spell_cost_extra", if (player.data.getInt("last_spell") == spellId) (player.data.getInt("spell_cost_extra") ?: 0) + 1 else 0)
            player.data.setInt("last_spell", spellId)

            RefreshRunnable(player.data, "spell_cost_extra") {
                player.data.setInt("spell_cost_extra", 0)
                player.data.setInt("last_spell", 0)
            }.schedule(100L)
        }

        if (spellId > 0) {
            if (player.foodLevel > cost) {
                player.playSound(player.location, Sound.ENTITY_EXPERIENCE_ORB_PICKUP, 1f, .5f)
                player.updateActionBar(
                    "${player.getLocalizedText("classes.${player.getWynnClass()}.spells.${if (player.isCloneClass) "${spellId}c" else spellId.toString()}")} Cast " +
                            "§3[§b-${cost}✺§3]"
                )
                player.foodLevel -= cost
            } else {
                player.playSound(player.location, Sound.BLOCK_ANVIL_PLACE, 1f, 1f)
                player.updateActionBar("§4Not enough mana!")
                return
            }
        } else {
            if (player.cooldown()) return
        }

        (spell as? Spell)?.cast(player) ?: (spell as BasePlayerSpell).tick()
    }

    private fun cost(player: Player, spellIndex: Int, cost: Int) =
        floor(ceil(cost * (1.0 - skillPercentage(player.getSkill(2)).let { if (player.hasScoreboardTag("pvp")) it.coerceAtMost(.55) else it }) + player.getId("spell_cost_raw_$spellIndex")) *
                (1.0 + player.getId("spell_cost_pct_$spellIndex") / 100.0) + (player.data.getInt("spell_cost_extra") ?: 0)).coerceAtLeast(1.0).toInt()
}