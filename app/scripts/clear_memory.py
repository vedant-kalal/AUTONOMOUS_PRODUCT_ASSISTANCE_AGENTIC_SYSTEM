from app.memory.memory_store import Memory_Functions
from app.core.config.settings import STM_NAMESPACE

store = Memory_Functions._get_store()
items = list(store.search(STM_NAMESPACE))
print(f"Found {len(items)} items. Deleting...")
for it in items:
    store.delete(STM_NAMESPACE, key=it.key)
print("Cleared.")
