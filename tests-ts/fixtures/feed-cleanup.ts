/**
 * Фікстура для cleanup фідів у БД: реєстрація feedId на видалення або деактивацію.
 * Cleanup виконується в teardown фікстури навіть при падінні тесту.
 */
import { test as base } from '@playwright/test';
import { deleteFeedById, deactivateFeedById } from '../utils/db-helper';
import { testConfig } from './env';

export const test = base.extend<{
  feedCleanup: {
    registerDelete: (feedId: string) => void;
    registerDeactivate: (feedId: string) => void;
  };
}>({
  feedCleanup: async ({}, use) => {
    const toDelete: string[] = [];
    const toDeactivate: string[] = [];
    const registerDelete = (feedId: string) => {
      if (feedId) toDelete.push(feedId);
    };
    const registerDeactivate = (feedId: string) => {
      if (feedId) toDeactivate.push(feedId);
    };
    await use({ registerDelete, registerDeactivate });
    // Teardown: завжди виконується, навіть при fail тесту
    if (!testConfig.dbHost || !testConfig.dbName) return;
    for (const id of toDeactivate) {
      try {
        await deactivateFeedById(id);
      } catch {
        /* ignore */
      }
    }
    for (const id of toDelete) {
      try {
        await deleteFeedById(id);
      } catch {
        /* ignore */
      }
    }
  },
});

export { expect } from '@playwright/test';
