<script lang="ts">
  export let limit: number;
  export let offset: number;
  export let length: number;

  let pageCount: number;
  let actualPage: number;
  let pages: number[] = [];

  function setOffset(event: Event, page: number) {
    event.preventDefault();
    offset = (page - 1) * limit;
  }

  $: {
    pages = [];
    pageCount = Math.ceil(length / (limit * 1.0));
    actualPage = Math.ceil(offset / (limit * 1.0)) + 1;

    for (let i = 1; i <= pageCount; i++) {
      pages.push(i);
    }
  }
</script>

<div class="d-flex w-100 justify-content-end">
  <nav aria-label="pagination">
    <ul class="pagination">
      <li class="page-item" class:disabled={actualPage == 1}>
        <button role="button" class="page-link" on:click={(event) => setOffset(event, 1)}>
          <span aria-hidden="true">{'\u00ab'}</span>
          <span class="sr-only">Prvá</span>
        </button>
      </li>
      <li class="page-item" class:disabled={actualPage == 1}>
        <button
          class="page-link"
          on:click={(event) => setOffset(event, actualPage - 1)}>
          <span aria-hidden="true">{'\u2039'}</span>
          <span class="sr-only">Predchádzajúca</span>
        </button>
      </li>
      {#each pages as page}
        <li class="page-item" class:active={page == actualPage}>
          <button
            class="page-link"
            on:click={(event) => setOffset(event, page)}>
            {page}
          </button>
        </li>
      {/each}
      <li class="page-item" class:disabled={actualPage == pageCount}>
        <button
          class="page-link"
          on:click={(event) => setOffset(event, actualPage + 1)}>
          <span aria-hidden="true">{'\u203A'}</span>
          <span class="sr-only">Ďalšia</span>
        </button>
      </li>
      <li class="page-item" class:disabled={actualPage == pageCount}>
        <button
          class="page-link"
          on:click={(event) => setOffset(event, pageCount)}>
          <span aria-hidden="true">{'\u00bb'}</span>
          <span class="sr-only">Posledná</span>
        </button>
      </li>
    </ul>
  </nav>
</div>
