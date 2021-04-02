from org.bukkit import Particle, Sound
from org.bukkit.entity import Mob, Player
from org.bukkit.potion import PotionEffect, PotionEffectType
from org.bukkit.util import Vector

from com.wynnlab.spells import PySpell

from java.lang import Math

class Spell(PySpell):
    def tick(self):
        if self.t == 0:
            if not self.player.getWorld().getBlockAt(self.player.getLocation().clone().subtract(0, 1, 0)).isEmpty() or not self.player.getWorld().getBlockAt(self.player.getLocation().clone().subtract(0, 2, 0)).isEmpty():
                #self.player.addScoreboardTag('escape')
                eye_dir = self.player.getEyeLocation().getDirection().clone()
                self.player.setVelocity(eye_dir.setY(Math.min(-.4 * Math.abs(eye_dir.getY()), -.4)).multiply(-4))

                self.player.playSound(self.player.getLocation(), Sound.ENTITY_BLAZE_SHOOT, 1, 1.2)
                self.player.spawnParticle(Particle.VILLAGER_HAPPY if self.clone else Particle.SQUID_INK, self.player.getLocation().clone().add(0, 1, 0), 10 if self.clone else 5, .3, 2, .3, .2)
                if self.clone:
                    self.player.spawnParticle(Particle.CLOUD, self.player.getLocation().clone().add(0, 1, 0), 5, .3, .3, .1)
            else:
                self.cancel()
            return

        if not self.player.isOnGround():
            self.delay()

            if self.player.isSneaking():
                self.player.setVelocity(self.player.getVelocity().clone().subtract(Vector(0, 1, 0)))
            elif self.player.getVelocity().getY() <= -.5:
                self.player.getVelocity().setY(-.5)
        else:
            if self.player.isSneaking():
                for i in range(0, 360, 60):
                    for j in range(9):
                        l = self.player.getLocation().clone().add(Math.sin(i * DEG2RAD) * j, 0, Math.cos(i * DEG2RAD) * j)
                        self.player.spawnParticle(Particle.SQUID_INK, l, 2, 0, 0, 0, .2)
                        self.player.spawnParticle(Particle.CLOUD, l, 2, 0, 0, 0, .2)
                        self.player.spawnParticle(Particle.CRIT, l, 2, 0, 0, 0, .3)

                self.player.playSound(self.player.getLocation(), Sound.ENTITY_GENERIC_EXPLODE, .5, 1.2)
                self.player.playSound(self.player.getLocation(), Sound.ENTITY_IRON_GOLEM_DEATH, 1, 1)

                for e in self.player.getNearbyEntities(8, 8, 8):
                    if isinstance(e, Player):
                        continue
                    if not isinstance(e, Mob):
                        continue

                    e.damage(4, self.player)
                    e.setNoDamageTicks(0)

            self.player.addPotionEffect(PotionEffect(PotionEffectType.SPEED, 3600, 2, True, False, True))