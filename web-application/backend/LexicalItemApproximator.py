import random
from gensim.models.keyedvectors import KeyedVectors
from sklearn.decomposition import IncrementalPCA
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from io import BytesIO


class LexicalItemApproximator:
    N_SIMILAR = 10
    N_DISSIMILAR = 2
    N_SUGGESTED_ITEMS = N_SIMILAR + N_DISSIMILAR

    def __init__(self, vectors: KeyedVectors):
        self.vectors = vectors
        self.selected_item = ""
        self.__start_items = []

        # sequences for undo
        self.selection_sequence: "list[str]" = []
        self.suggestions_sequence: "list['list[str]']" = []

        # used for result evaluation and persistence
        self.most_similar_of_suggested_sequence: "list[str]" = []
        self.y_vals_selection: "list[float]" = []
        self.y_vals_suggestions_avg: "list[float]" = []
        self.y_vals_closest: "list[float]" = []

        # for plotting suggestions in 2d space
        self.plot_is_initialized = False
        self.y_vals = []
        self.x_vals = []
        self.labels = []
        self.plot_pca = None

    @property
    def start_items(self):
        if(self.__start_items): return self.__start_items
        # Randomly choose the first suggested item
        suggestions: "list[str]" = [
            random.choice(self.vectors.index_to_key)]

        # Calculate position and width for a slice whose width is one percent of the length of the item list and whose center is at 67 percent of the length
        assert(len(self.vectors) >= 100)
        slice_width = len(self.vectors) / 100
        slice_position = int(slice_width * 67 - slice_width / 2)

        for _ in range(LexicalItemApproximator.N_SUGGESTED_ITEMS - 1):
            items_sorted = self._get_items_sorted_by_similarity_to(
                # Get a list sorted by similarity to the last item added to the suggestions
                item=suggestions[-1], excluded_items=set(suggestions))
            # Choose a random item from the sliced sorted similarity list
            suggestions.append(random.choice(
                items_sorted[slice_position: int(slice_position + slice_width)]))

        self.suggestions_sequence.append(suggestions)

        self.__start_items = suggestions
        return suggestions

    @property
    def iterations(self):
        return len(self.selection_sequence)

    @property
    def excluded_items(self):
        """
        Returns:
            set[str]: All items suggested previously
        """
        return {item
        for suggestions in self.suggestions_sequence
        for item in suggestions}

    @property
    def items_to_plot(self):
        return self.suggestions_sequence[-1] if self.suggestions_sequence else []

    def suggest_items(self):
        # self.selected_item is the item selected in previous iteration. Do not continue if it is not set.
        if not self.selected_item: return

        items_sorted = self._get_items_sorted_by_similarity_to(
            self.selected_item, self.excluded_items)

        if len(items_sorted) < LexicalItemApproximator.N_SUGGESTED_ITEMS:
            return []

        similar_items = items_sorted[:LexicalItemApproximator.N_SIMILAR]

        # Take the rest as random items of 100 items in the middle of sorted dist list
        # (These are considered relatively dissimilar)
        slice_middle = int(len(items_sorted) / 2 - 50)
        dissimilar_items = random.sample(
            items_sorted[slice_middle: slice_middle + 100], k=LexicalItemApproximator.N_DISSIMILAR)

        suggestions = similar_items + dissimilar_items

        # Record suggestion history for undo function and excluded items
        self.suggestions_sequence.append(suggestions)

        return suggestions

    def select_item(self, item: str):
        self.selected_item = item
        self.selection_sequence.append(item)

    def undo(self):
        """Sets selected item to previous selected item and deletes previous suggestions from suggestion history.
        """
        self.suggestions_sequence.pop()
        self.selection_sequence.pop()
        self.selected_item = self.selection_sequence[-1] if self.selection_sequence else ""

# region plot

    def init_plot(self):
        if(self.plot_is_initialized): return
        num_dimensions = 2

        # extract the items & their vectors, as numpy arrays
        vectors: np.ndarray = np.array(self.vectors.vectors)

        self.labels = np.array(self.vectors.index_to_key)

        # reduce using pca
        pca = IncrementalPCA(n_components=num_dimensions, batch_size=10)
        self.plot_pca = pca
        vectors = pca.fit_transform(vectors)

        self.x_vals = [v[0] for v in vectors]
        self.y_vals = [v[1] for v in vectors]

        self.plot_is_initialized = True

    def get_plot_image(self) -> bytes:
        self.init_plot()
        items = self.items_to_plot
        matplotlib.use('Agg')
        fig = plt.figure(figsize=(12, 12))
        plt.scatter(self.x_vals, self.y_vals, alpha=.2)
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)

        selected_indices = []
        for item in items:
            selected_index = np.where(self.labels == item)[
                0][0] 
            selected_indices.append(selected_index)
        for i in selected_indices:
            plt.annotate(text=self.labels[i].replace("_", " "), xy=(
                self.x_vals[i], self.y_vals[i]), fontsize=14, fontweight='bold', alpha=.7)
            plt.scatter(self.x_vals[i], self.y_vals[i], color='red', alpha=.5)

        # plot target item
        if self.selected_item in self.labels:
            target_index = np.where(self.labels == self.selected_item)[0][0]
            plt.annotate(text=self.labels[target_index].replace("_", " "), xy=(
                self.x_vals[target_index], self.y_vals[target_index]), fontsize=20, fontweight='bold', alpha=.7)
            plt.scatter(self.x_vals[target_index],
                        self.y_vals[target_index], color='green', s=100, alpha=.5)

        figdata = BytesIO()
        fig.savefig(figdata, format='png')
        plt.close(fig)

        return figdata.getvalue()

    def get_result_plot_image(self, result: str):
        """Records data for result evaluation (most_similar_of_suggested_sequence) and returns a result plot as png image.

        Args:
            result (str): The target item

        Returns:
            bytes: png image
        """
        import math
        if len(self.selection_sequence) < len(self.suggestions_sequence):
            self.suggestions_sequence.pop()
        
        x_vals = range(1, self.iterations + 1)
        self.y_vals_selection = [self.vectors.similarity(
            result, item) for item in self.selection_sequence]
        self.y_vals_suggestions_avg = []
        self.y_vals_closest = []
        for suggestions in self.suggestions_sequence:
            suggestions_vectors = np.array(
                [self.vectors[item] for item in suggestions])
            dists = np.dot(suggestions_vectors, np.ravel(self.vectors[result])) / (
                np.linalg.norm(suggestions_vectors, axis=1) * np.linalg.norm(self.vectors[result]))

            self.y_vals_suggestions_avg.append(np.average(dists))
            index_closest = np.argsort(dists)[::-1][0]
            self.most_similar_of_suggested_sequence.append(
                suggestions[index_closest])
            self.y_vals_closest.append(dists[index_closest])

        matplotlib.use('Agg')

        assert(len(self.y_vals_selection) == len(
            self.y_vals_suggestions_avg) == len(self.y_vals_closest) > 0)


        iterations = len(self.y_vals_selection)

        x_vals = range(1, iterations + 1)

        fig, (ax, ax2) = plt.subplots(2, 1, sharex=True,
            gridspec_kw={'height_ratios': [10, 1]})

        ax.plot(x_vals, self.y_vals_selection, marker='^',
                    label='selected item', ls=(0, (1, 10)), alpha=.5, color='k')
        ax.plot(x_vals, self.y_vals_closest, marker='o',
                    label='most similar of suggested', ls=(0, (5, 10)), alpha=.5, color='k')
        ax.plot(x_vals, self.y_vals_suggestions_avg, marker='o',
                    label='average of suggested', alpha=.5, color='k')
        ax.title.set_text(f'Target Item: {result.replace("_", " ").title()}')
        ax.legend(loc='best', title='cosine similarity for')
        plt.xlabel('iteration')
        ax.set_ylabel('cosine similarity to target')

        # hide the spines between ax and ax2
        ax.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax.xaxis.tick_top()
        ax.tick_params(labeltop=False)  # don't put tick labels at the top
        ax2.xaxis.tick_bottom()

        ax.set_ylim(math.floor(min(self.y_vals_closest + self.y_vals_selection +
                    self.y_vals_suggestions_avg)*10)/10 - .02, 1)  # data
        ax2.set_ylim(0, .01)  # 0 to 0.1
        plt.xlim(1, iterations)

        d = .015  # how big to make the lines in axes coordinates
        # arguments to pass to plot, just so we don't keep repeating them
        kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
        ax.plot((-d, +d), (-d, -d), **kwargs)        # top-left line
        ax.plot((1 - d, 1 + d), (-d, -d), **kwargs)  # top-right line

        kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
        ax2.plot((-d, +d), (1 - d, 1 - d), **kwargs)  # bottom-left line
        ax2.plot((1 - d, 1 + d), (1 - d, 1 - d), **kwargs)  # bottom-right line

        plt.subplots_adjust(hspace=.07)

        ax.xaxis.set_major_locator(plt.MultipleLocator(1))
        ax.yaxis.set_major_locator(plt.MultipleLocator(.1))
        ax2.yaxis.set_major_locator(plt.MultipleLocator(.1))

        figdata = BytesIO()
        fig.savefig(figdata, format='png')
        plt.close(fig)

        return figdata.getvalue()

# endregion

# region 'private' methods

    def _get_items_sorted_by_similarity_to(self, item: str, excluded_items: "set[str]" = None):
        """Generates a list of lexical items sorted by similarity to a given item

        Args:
            item (str): The lexical whose similarity the list will be sorted by
            excluded_items (set[str], optional): The items to be excluded from the list. Defaults to None.

        Returns:
            list[str]: The list of items sorted by similarity to parameter item
        """
        if excluded_items: excluded_items.update([item])
        else: excluded_items = {item}
        # self.vectors is the instance of the Gensim KeyedVectors class with the vectors generated before.
        # Ensures vector lengths are available at self.vectors.norms 
        self.vectors.fill_norms()
        # The vector for item can simply be accessed from the KeyedVectors object with item as key 
        cos_similarities = np.dot(self.vectors.vectors,
                       self.vectors[item]) / self.vectors.norms

        # Get indices of the list sorted by cosine similarity
        indices_sorted_similarities = np.argsort(-cos_similarities)

        items_sorted: "list[str]" = [
            # self.vectors.index_to_key contains all items that can be accessed with their index as key
            self.vectors.index_to_key[i]
            for i in indices_sorted_similarities 
            # ignore (don't return) items from excluded item list
            if self.vectors.index_to_key[i] not in excluded_items
        ]

        return items_sorted

# endregion
