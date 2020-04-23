from enum import Enum


class RedisKey(Enum):
    TASKS_IN_PROGRESS = 'TASKS_IN_PROGRESS'
    SOLVED_TASKS = 'SOLVED_TASKS'
    FALLEN_TASKS = 'FALLEN_TASKS'
