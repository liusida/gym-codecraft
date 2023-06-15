from gymnasium.envs.registration import register

register(
    id="gym_codecraft/CodeCraft-v0",
    entry_point="gym_codecraft.envs:CodeCraftEnv",
)